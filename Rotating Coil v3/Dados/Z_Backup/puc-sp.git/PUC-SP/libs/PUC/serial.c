/*
 * This module handles the communication with the external world, using the
 * UART peripheral.
 */

#include "common.h"
#include "ports.h"
#include "sync.h"

#define SERIAL_HEADER       1u          // Destination byte
#define WHOLE_HEADER        (SERIAL_HEADER+BSMP_HEADER_SIZE)    // = 4
#define SERIAL_CSUM         1u          // How many bytes of checksum
#define BCAST_ADDR          255u        // Broadcast Address
#define MASTER_ADDR         0u          // Address of the master of the network

// Maximum packet: 16392
// Header (1) + BSMP Header (3) + Max Body (curve block: 16387) + Csum (1)
#define BUFFER_LEN          17000       // Enough for all packets expected
#define MAX_REMAINING       (BUFFER_LEN - WHOLE_HEADER)

static enum rx_stage
{
    RX_HEADER,
    RX_BODY,
}rx_stage = RX_HEADER;

// Buffers to send and receive messages
static struct serial_buffer
{
    uint8_t  data[BUFFER_LEN];
    uint32_t size;
}
recv_buffer = {.data = {0}, .size = 0},
send_buffer = {.data = {0}, .size = 0};

// Wrappers around the buffers, used to pass the message to the BSMP instance
static struct bsmp_raw_packet
recv_packet = {.data = &recv_buffer.data[SERIAL_HEADER]},
send_packet = {.data = &send_buffer.data[SERIAL_HEADER]};

// This device's address in the serial network
static uint8_t serial_address;
static bsmp_server_t *server;

// IRQ cofigurations

static const NVIC_InitTypeDef TIMER_NVIC_INIT = {
    .NVIC_IRQChannel                    = SERIAL_TIMER_IRQn,
    .NVIC_IRQChannelPreemptionPriority  = SERIAL_TIMER_PRIO,
    .NVIC_IRQChannelSubPriority         = SERIAL_TIMER_SUB_PRIO,
    .NVIC_IRQChannelCmd                 = ENABLE,
};

static const NVIC_InitTypeDef UART_NVIC_INIT = {
    .NVIC_IRQChannel                    = SERIAL_UART_IRQn,
    .NVIC_IRQChannelPreemptionPriority  = SERIAL_UART_PRIO,
    .NVIC_IRQChannelSubPriority         = SERIAL_UART_SUB_PRIO,
    .NVIC_IRQChannelCmd                 = ENABLE,
};

static const NVIC_InitTypeDef DMA_RX_NVIC_INIT = {
    .NVIC_IRQChannel                    = SERIAL_DMA_RX_IRQn,
    .NVIC_IRQChannelPreemptionPriority  = SERIAL_DMA_RX_PRIO,
    .NVIC_IRQChannelSubPriority         = SERIAL_DMA_RX_SUB_PRIO,
    .NVIC_IRQChannelCmd                 = ENABLE,
};

static const NVIC_InitTypeDef DMA_TX_NVIC_INIT = {
    .NVIC_IRQChannel                    = SERIAL_DMA_TX_IRQn,
    .NVIC_IRQChannelPreemptionPriority  = SERIAL_DMA_TX_PRIO,
    .NVIC_IRQChannelSubPriority         = SERIAL_DMA_TX_SUB_PRIO,
    .NVIC_IRQChannelCmd                 = ENABLE,
};

// Peripheral configurations

static const TIM_TimeBaseInitTypeDef TIMER_INIT = {
    .TIM_Period                 = UART_TIMER_PERIOD,
    .TIM_Prescaler              = UART_TIMER_PRESCALER,
    .TIM_ClockDivision          = 0,
    .TIM_CounterMode            = TIM_CounterMode_Up,
};

static const USART_InitTypeDef USART_INIT = {
    .USART_WordLength           = USART_WordLength_8b,
    .USART_StopBits             = USART_StopBits_1,
    .USART_Parity               = USART_Parity_No,
    .USART_HardwareFlowControl  = USART_HardwareFlowControl_None,
    .USART_Mode                 = (USART_Mode_Tx | USART_Mode_Rx),
    .USART_BaudRate             = UART_BAUD,
};

static const DMA_InitTypeDef DMA_RX_INIT = {
    .DMA_Channel            = SERIAL_DMA_RX_CHN,
    .DMA_DIR                = DMA_DIR_PeripheralToMemory,
    .DMA_Memory0BaseAddr    = (uint32_t)recv_buffer.data,
    .DMA_BufferSize         = WHOLE_HEADER,
    .DMA_PeripheralBaseAddr = (uint32_t)&SERIAL_UART->DR,
    .DMA_PeripheralInc      = DMA_PeripheralInc_Disable,
    .DMA_MemoryInc          = DMA_MemoryInc_Enable,
    .DMA_PeripheralDataSize = DMA_PeripheralDataSize_Byte,
    .DMA_MemoryDataSize     = DMA_MemoryDataSize_Byte,
    .DMA_Mode               = DMA_Mode_Normal,
    .DMA_Priority           = DMA_Priority_High,
    .DMA_MemoryBurst        = DMA_MemoryBurst_Single,
    .DMA_PeripheralBurst    = DMA_PeripheralBurst_Single,
    .DMA_FIFOMode           = DMA_FIFOMode_Disable,
    //.DMA_FIFOThreshold      = 0,
};

static const DMA_InitTypeDef DMA_TX_INIT = {
    .DMA_Channel            = SERIAL_DMA_TX_CHN,
    .DMA_DIR                = DMA_DIR_MemoryToPeripheral,
    .DMA_Memory0BaseAddr    = (uint32_t)send_buffer.data,
    .DMA_BufferSize         = 0,
    .DMA_PeripheralBaseAddr = (uint32_t)&SERIAL_UART->DR,
    .DMA_PeripheralInc      = DMA_PeripheralInc_Disable,
    .DMA_MemoryInc          = DMA_MemoryInc_Enable,
    .DMA_PeripheralDataSize = DMA_PeripheralDataSize_Byte,
    .DMA_MemoryDataSize     = DMA_MemoryDataSize_Byte,
    .DMA_Mode               = DMA_Mode_Normal,
    .DMA_Priority           = DMA_Priority_High,
    .DMA_MemoryBurst        = DMA_MemoryBurst_Single,
    .DMA_PeripheralBurst    = DMA_PeripheralBurst_Single,
    .DMA_FIFOMode           = DMA_FIFOMode_Disable,
    //.DMA_FIFOThreshold      = 0,
};

static inline uint32_t min (uint32_t a, uint32_t b)
{
    return a < b ? a : b;
}

static inline bool csum_ok (uint8_t *data, uint32_t len)
{
    /*uint32_t __UADD8    (   uint32_t    val1,
    uint32_t    val2
    ) */

    // Calculate checksum optimized
    /*uint32_t temp, count, *p;
    count = recv_buffer.size;
    p = (uint32_t *) recv_buffer.data;

    while(count > 4)
    {
        temp = *p++;        // Point to 4-bytes from recv_buffer

        csum += temp;       // Sum each one of the four bytes
        csum += temp >> 8;
        csum += temp >> 16;
        csum += temp >> 24;

        count -= 4;
    }

    while(count > 0)        // Sum unaligned bytes
        csum += ((uint8_t*)p)[--count];*/

    uint8_t csum = 0;
    while(len--)
        csum += *data++;
    return !csum;
}

static inline void clear_uart_errors (void)
{
    /* Error flags are cleared by software sequence: a read operation to
     * USART_SR register (USART_GetFlagStatus()) followed by a read operation to
     * USART_DR register (USART_ReceiveData()) */

    // Doesn't matter which flag is specified here. ORE = Overrun Error
    (void)USART_GetITStatus(SERIAL_UART, USART_IT_ORE_RX);
    (void)USART_GetFlagStatus(SERIAL_UART, USART_FLAG_ORE);
    (void)USART_ReceiveData(SERIAL_UART);
}

// Initialize UART2, DMA0, DMA1, DMA2
void serial_init (bsmp_server_t *server_handle)
{
    serial_address = get_serial_address();  // Configured with jumpers
    server         = server_handle;         // Pointer to BSMP library instance

    // Configure interrupts
    NVIC_Init((NVIC_InitTypeDef*) &TIMER_NVIC_INIT);    // Timeout
    NVIC_Init((NVIC_InitTypeDef*) &UART_NVIC_INIT);     // UART Error interrupt
    NVIC_Init((NVIC_InitTypeDef*) &DMA_RX_NVIC_INIT);   // DMA RX complete
    NVIC_Init((NVIC_InitTypeDef*) &DMA_TX_NVIC_INIT);   // DMA TX complete

    // Configure peripherals
    TIM_TimeBaseInit(SERIAL_TIMER, (TIM_TimeBaseInitTypeDef*) &TIMER_INIT);
    DMA_Init(SERIAL_DMA_RX, (DMA_InitTypeDef*) &DMA_RX_INIT);
    DMA_Init(SERIAL_DMA_TX, (DMA_InitTypeDef*) &DMA_TX_INIT);

    USART_OverSampling8Cmd(SERIAL_UART, ENABLE);        // **BEFORE** USART_Init
    USART_Init(SERIAL_UART, (USART_InitTypeDef*) &USART_INIT);

    // Clear interrupts
    TIM_ClearITPendingBit(SERIAL_TIMER, TIM_IT_Update);
    DMA_ClearITPendingBit(SERIAL_DMA_RX, SERIAL_DMA_RX_IF);
    DMA_ClearITPendingBit(SERIAL_DMA_TX, SERIAL_DMA_TX_IF);

    // Enable peripherals interrupts
    TIM_ITConfig(SERIAL_TIMER, TIM_IT_Update, ENABLE);
    DMA_ITConfig(SERIAL_DMA_RX, DMA_IT_TC, ENABLE);
    DMA_ITConfig(SERIAL_DMA_TX, DMA_IT_TC, ENABLE);
    USART_ITConfig(SERIAL_UART, USART_IT_ERR, ENABLE);
    USART_DMACmd(SERIAL_UART, USART_DMAReq_Rx | USART_DMAReq_Tx, ENABLE);

    // Enable reception
    DMA_Cmd(SERIAL_DMA_RX, ENABLE);
    USART_Cmd(SERIAL_UART, ENABLE); // UART **AFTER** DMA
}

// Packet received
static void process_packet (void)
{
    uint8_t csum = 0;
    unsigned int i;

    // Get destination of the received message
    uint8_t dest = recv_buffer.data[0];

    // Calculate checksum
    if(!csum_ok(recv_buffer.data, recv_buffer.size))
        return;

    // The message is OK. Check destination. If it isn't for me, ignore it.
    if(dest != serial_address && dest != BCAST_ADDR)
        return;

    // Prepare message to be processed
    recv_packet.len = recv_buffer.size - SERIAL_HEADER - SERIAL_CSUM;

    // Perform the requested command and prepare an answer
    bsmp_process_packet(server, &recv_packet, &send_packet);

    if(dest != serial_address)  // Don't answer broadcast/multicast messages
        return;

    // Prepare buffer for the answer
    send_buffer.data[0] = MASTER_ADDR;
    send_buffer.size    = SERIAL_HEADER + send_packet.len + SERIAL_CSUM;

    // Calculate checksum
    csum = 0;
    for(i = 0; i < send_packet.len + SERIAL_HEADER; ++i)
        csum -= send_buffer.data[i];

    send_buffer.data[SERIAL_HEADER + send_packet.len] = csum;

    // Send packet
    SERIAL_DMA_TX->NDTR = send_buffer.size;
    uart_enable(true);
    DMA_Cmd(SERIAL_DMA_TX, ENABLE);
}

// RX DMA is done
SERIAL_DMA_RX_IRQ
{
    if(rx_stage == RX_HEADER)   // Header arrived
    {
        // Prepare next transfer (body)
        rx_stage = RX_BODY;

        // Remaining bytes to be received
        uint8_t *d = recv_buffer.data;
        uint32_t remaining;
        remaining = min((d[2] << 8) + d[3] + SERIAL_CSUM, MAX_REMAINING);

        // Set total buffer size
        recv_buffer.size = WHOLE_HEADER + remaining;

        SERIAL_DMA_RX->M0AR = (uint32_t) (recv_buffer.data + WHOLE_HEADER);
        SERIAL_DMA_RX->NDTR = remaining;

        // Start timeout
        SERIAL_TIMER->CNT = 0;
        TIM_Cmd(SERIAL_TIMER, ENABLE);
    }
    else                        // Rest of the packet arrived
    {
        // Stop timeout
        TIM_Cmd(SERIAL_TIMER, DISABLE);

        // Was it aborted by the timer?
        recv_buffer.size -= SERIAL_DMA_RX->NDTR;

        // Process the packet that arrived
        process_packet();

        // Prepare next transfer (another header)
        rx_stage = RX_HEADER;
        SERIAL_DMA_RX->M0AR = (uint32_t) recv_buffer.data;
        SERIAL_DMA_RX->NDTR = WHOLE_HEADER;
    }

    DMA_ClearITPendingBit(SERIAL_DMA_RX, SERIAL_DMA_RX_IF); // Clear flag

    // Next transfer
    clear_uart_errors();
    DMA_Cmd(SERIAL_DMA_RX, ENABLE);
}

// TX DMA is done
SERIAL_DMA_TX_IRQ
{
    while(!USART_GetFlagStatus(SERIAL_UART, USART_FLAG_TC));
    uart_enable(false);
    DMA_ClearITPendingBit(SERIAL_DMA_TX, SERIAL_DMA_TX_IF);
}

// TX/RX error
SERIAL_UART_IRQ
{
    clear_uart_errors();
    USART_ClearITPendingBit(SERIAL_UART, USART_IT_ERR);
}

// Timeout
SERIAL_TIMER_IRQ
{
    TIM_Cmd(SERIAL_TIMER, DISABLE);     // Stop timeout
    DMA_Cmd(SERIAL_DMA_RX, DISABLE);    // Stop DMA
    TIM_ClearITPendingBit(SERIAL_TIMER, TIM_IT_Update);
}
