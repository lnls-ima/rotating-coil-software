#include "ports.h"

#include <stdint.h>
#include <stdbool.h>
#include "stm32f4xx.h"

void ports_init (void)
{
    // Ports initialization

    // Default for every port (TRISx) is input (1)
    // There are pins that can be changed to output later (for example, pins of
    // the parallel port)
    GPIO_InitTypeDef GPIO_In    = { .GPIO_Mode  = GPIO_Mode_IN,
                                    .GPIO_OType = GPIO_OType_PP,
                                    .GPIO_Speed = GPIO_Speed_100MHz,
                                    .GPIO_PuPd  = GPIO_PuPd_NOPULL};

    GPIO_InitTypeDef GPIO_Out   = { .GPIO_Mode  = GPIO_Mode_OUT,
                                    .GPIO_Speed = GPIO_Speed_100MHz };

    GPIO_InitTypeDef GPIO_AF    = { .GPIO_Mode  = GPIO_Mode_AF,
                                    .GPIO_Speed = GPIO_Speed_100MHz };


    /*
     * Port A
     *
     * Bit  0 - RESET        - input    (JTAG reset signal)
     * Bit  1 - ETH_REF_CLK  - AF       (Ethernet REF_CLK)
     * Bit  2 - ETH_MDIO     - AF       (Ethernet MDIO)
     * Bit  3 - ID3          - input    (PUC Serial Address)
     * Bit  4 - CSF          - output   (Flash Chip Select)
     * Bit  5 - SCLKF        - AF       (Flash SPI1 CLK)
     * Bit  6 - MISOF        - AF       (Flash SPI1 MISO)
     * Bit  7 - ETH_CSR_DV   - AF       (Ethernet CRS_DV)
     * Bit  8 -
     * Bit  9 - TX           - AF       (USART1 TX (RS-485))
     * Bit 10 - RX           - AF       (USART1 RX (RS-485))
     * Bit 11 - DE           - output   (RS-485 Driver Enable)
     * Bit 12 -
     * Bit 13 - TMS          - Don't touch!
     * Bit 14 - TCK          - Don't touch!
     * Bit 15 - TDI          - Don't touch!
     */

    // Inputs
    GPIO_In.GPIO_Pin = GPIO_Pin_0 | GPIO_Pin_3;
    GPIO_Init(GPIOA, &GPIO_In);

    // Outputs
    GPIO_Out.GPIO_Pin = GPIO_Pin_4 | GPIO_Pin_11;
    GPIO_Init(GPIOA, &GPIO_Out);

    // Alternate functions
    GPIO_AF.GPIO_Pin = GPIO_Pin_1 | GPIO_Pin_2 | GPIO_Pin_5 | GPIO_Pin_6 |
                       GPIO_Pin_7 | GPIO_Pin_9 | GPIO_Pin_10;
    GPIO_Init(GPIOA, &GPIO_AF);

    GPIO_PinAFConfig(GPIOA, GPIO_PinSource1, GPIO_AF_ETH);
    GPIO_PinAFConfig(GPIOA, GPIO_PinSource2, GPIO_AF_ETH);
    GPIO_PinAFConfig(GPIOA, GPIO_PinSource5, GPIO_AF_SPI1);
    GPIO_PinAFConfig(GPIOA, GPIO_PinSource6, GPIO_AF_SPI1);
    GPIO_PinAFConfig(GPIOA, GPIO_PinSource7, GPIO_AF_ETH);
    GPIO_PinAFConfig(GPIOA, GPIO_PinSource9, GPIO_AF_USART1);
    GPIO_PinAFConfig(GPIOA, GPIO_PinSource10, GPIO_AF_USART1);

    /*
     * Port B
     *
     * Bit  0 - CLEAR_INT   - output    (Clear interrupt flags on boards)
     * Bit  1 - ID4         - input     (PUC Serial Address)
     * Bit  2 - BOOT1       - input     (Connected to ground)
     * Bit  3 - TDO         - Don't touch!
     * Bit  4 - TRST        - Don't touch!
     * Bit  5 - MOSIF       - AF        (Flash SPI1 MOSI)
     * Bit  6 - PDIR        - output    (Parallel direction selector)
     * Bit  7 -
     * Bit  8 -
     * Bit  9 - CSR         - output    (RAM Chip Select)
     * Bit 10 - SCLKR       - AF        (RAM SPI2 CLK)
     * Bit 11 - ETH_TX_EN   - AF        (Ethernet TX_EN)
     * Bit 12 - ETH_TXD0    - AF        (Ethernet TXD0)
     * Bit 13 - ETH_TXD1    - AF        (Ethernet TXD1)
     * Bit 14 - PSYNI       - output    (Software SYNI (to read ADCs))
     * Bit 15 - PSYNO         output    (Software SYNO (to write DACs))
     */
    GPIO_In.GPIO_Pin = GPIO_Pin_1 | GPIO_Pin_2;
    GPIO_Init(GPIOB, &GPIO_In);

    GPIO_Out.GPIO_Pin = GPIO_Pin_0 | GPIO_Pin_6 | GPIO_Pin_9 | GPIO_Pin_14 |
                        GPIO_Pin_15;
    GPIO_Init(GPIOB, &GPIO_Out);

    GPIO_AF.GPIO_Pin = GPIO_Pin_5 | GPIO_Pin_10 | GPIO_Pin_11 | GPIO_Pin_12 |
                       GPIO_Pin_13;
    GPIO_Init(GPIOB, &GPIO_AF);

    GPIO_PinAFConfig(GPIOB, GPIO_PinSource5, GPIO_AF_SPI1);
    GPIO_PinAFConfig(GPIOB, GPIO_PinSource10, GPIO_AF_SPI2);
    GPIO_PinAFConfig(GPIOB, GPIO_PinSource11, GPIO_AF_ETH);
    GPIO_PinAFConfig(GPIOB, GPIO_PinSource12, GPIO_AF_ETH);
    GPIO_PinAFConfig(GPIOB, GPIO_PinSource13, GPIO_AF_ETH);

    /*
     * Port C
     *
     * Bit  0 -
     * Bit  1 - ETH_MDC     - AF        (Ethernet MDC)
     * Bit  2 - MISOR       - AF        (RAM SPI2 MISO)
     * Bit  3 - MOSIR       - AF        (RAM SPI2 MOSI)
     * Bit  4 - ETH_RXD0    - AF        (Ethernet RXD0)
     * Bit  5 - ETH_RXD1    - AF        (Ethernet RXD1)
     * Bit  6 - ETH_INT     - input
     * Bit  7 - ETH_INT     - input
     * Bit  8 - ETH_INT     - input
     * Bit  9 - ESYNI       - input     (ESYNI Interrupt)
     * Bit 10 - PCSP0       - output    (Parallel port Chip Select)
     * Bit 11 - PCSP1       - output    (Parallel port Chip Select)
     * Bit 12 - PCSP2       - output    (Parallel port Chip Select)
     * Bit 13 - ID0         - input     (PUC Serial Address)
     * Bit 14 - ID1         - input     (PUC Serial Address)
     * Bit 15 - ID2         - input     (PUC Serial Address)
     */
    GPIO_In.GPIO_Pin = GPIO_Pin_6 | GPIO_Pin_7 | GPIO_Pin_8 | GPIO_Pin_9 |
                       GPIO_Pin_13 | GPIO_Pin_14 | GPIO_Pin_15;
    GPIO_Init(GPIOC, &GPIO_In);

    GPIO_Out.GPIO_Pin = GPIO_Pin_10 | GPIO_Pin_11 | GPIO_Pin_12;
    GPIO_Init(GPIOC, &GPIO_Out);

    GPIO_AF.GPIO_Pin = GPIO_Pin_1 | GPIO_Pin_2 | GPIO_Pin_3 | GPIO_Pin_4 |
                       GPIO_Pin_5;
    GPIO_Init(GPIOC, &GPIO_AF);

    GPIO_PinAFConfig(GPIOC, GPIO_PinSource1, GPIO_AF_ETH);
    GPIO_PinAFConfig(GPIOC, GPIO_PinSource2, GPIO_AF_SPI2);
    GPIO_PinAFConfig(GPIOC, GPIO_PinSource3, GPIO_AF_SPI2);
    GPIO_PinAFConfig(GPIOC, GPIO_PinSource4, GPIO_AF_ETH);
    GPIO_PinAFConfig(GPIOC, GPIO_PinSource5, GPIO_AF_ETH);

    /*
     * Port D
     *
     * Bits 7~0   - PD7~0   - input     (Parallel port data)
     * Bit  8     - U3TX    - AF        (Uart 3 TX)
     * Bit  9     - U3RX    - AF        (Uart 3 RX)
     * Bit 10     - ESYNO   - input     (ESYNO Interrupt)
     * Bit 14     - ETH_INT - input
     * Bit 15     - ETH_INT - input
     */
    GPIO_In.GPIO_Pin = GPIO_Pin_0 | GPIO_Pin_1 | GPIO_Pin_2 | GPIO_Pin_3 |
                       GPIO_Pin_4 | GPIO_Pin_5 | GPIO_Pin_6 | GPIO_Pin_7 |
                       GPIO_Pin_10 | GPIO_Pin_14 | GPIO_Pin_15;
    GPIO_Init(GPIOD, &GPIO_In);

    GPIO_AF.GPIO_Pin = GPIO_Pin_8 | GPIO_Pin_9;
    GPIO_Init(GPIOD, &GPIO_AF);

    GPIO_PinAFConfig(GPIOD, GPIO_PinSource8, GPIO_AF_USART3);   // USART3_TX
    GPIO_PinAFConfig(GPIOD, GPIO_PinSource9, GPIO_AF_USART3);   // USART3_RX

    /*
     * Port E
     *
     * Bit  0 - EXTI0       - input     (Board #0 Interrupt)
     * Bit  1 - EXTI1       - input     (Board #1 Interrupt)
     * Bit  2 - EXTI2       - input     (Board #2 Interrupt)
     * Bit  3 - EXTI3       - input     (Board #3 Interrupt)
     * Bit  4 -
     * Bit  5 - LED1        - output    (Debug Led #1)
     * Bit  6 - LED2        - output    (Debug Led #2)
     * Bit  7 - PL0         - output    (Board Select, bit 0)
     * Bit  8 - PL1         - output    (Board Select, bit 1)
     * Bit  9 - PCSS0       - output    (Board Chip Select, bit 0)
     * Bit 10 - PCSS1       - output    (Board Chip Select, bit 1)
     * Bit 11 - PCSS2       - output    (Board Chip Select, bit 2)
     * Bit 12 - PCLK        - AF        (Modules SPI4 CLK)
     * Bit 13 - PDI         - AF        (Modules SPI4 MISO)
     * Bit 14 - PDO         - AF        (Modules SPI4 MOSI)
     * Bit 15 -
     */
    GPIO_In.GPIO_Pin = GPIO_Pin_0 | GPIO_Pin_1 | GPIO_Pin_2 | GPIO_Pin_3;
    GPIO_Init(GPIOE, &GPIO_In);

    GPIO_Out.GPIO_Pin = GPIO_Pin_5 | GPIO_Pin_6 | GPIO_Pin_7 | GPIO_Pin_8 |
                        GPIO_Pin_9 | GPIO_Pin_10 | GPIO_Pin_11;
    GPIO_Init(GPIOE, &GPIO_Out);

    GPIO_AF.GPIO_Pin = GPIO_Pin_12 | GPIO_Pin_13 | GPIO_Pin_14;
    GPIO_Init(GPIOE, &GPIO_AF);

    GPIO_PinAFConfig(GPIOE, GPIO_PinSource12, GPIO_AF_SPI4);
    GPIO_PinAFConfig(GPIOE, GPIO_PinSource13, GPIO_AF_SPI4);
    GPIO_PinAFConfig(GPIOE, GPIO_PinSource14, GPIO_AF_SPI4);
}

void uart_enable (bool enable)
{
    GPIO_WriteBit(GPIOA, GPIO_Pin_11, enable);
}

uint8_t get_serial_address (void)
{
    uint8_t address = 0;
    address |= (GPIO_ReadInputDataBit(GPIOB, GPIO_Pin_1) << 4) & 0x10;
    address |= (GPIO_ReadInputDataBit(GPIOA, GPIO_Pin_3) << 3) & 0x08;
    address |= (GPIO_ReadInputDataBit(GPIOC, GPIO_Pin_15) << 2) & 0x04;
    address |= (GPIO_ReadInputDataBit(GPIOC, GPIO_Pin_14) << 1) & 0x02;
    address |= (GPIO_ReadInputDataBit(GPIOC, GPIO_Pin_13) << 0) & 0x01;
    address = (~address) & 0x1F;
    //address |= (GPIO_ReadInputData(GPIOC) >> 13) & 0x07;
    return address;
}

void chip_select(uint8_t chip)
{
    GPIO_WriteBit(GPIOE, GPIO_Pin_9, (chip >> 0) & 0x01);
    GPIO_WriteBit(GPIOE, GPIO_Pin_10, (chip >> 1) & 0x01);
    GPIO_WriteBit(GPIOE, GPIO_Pin_11, (chip >> 2) & 0x01);
}

void parallel_select (uint8_t parallel)
{
    GPIO_WriteBit(GPIOC, GPIO_Pin_10, (parallel >> 0) & 0x01);
    GPIO_WriteBit(GPIOC, GPIO_Pin_11, (parallel >> 1) & 0x01);
    GPIO_WriteBit(GPIOC, GPIO_Pin_12, (parallel >> 2) & 0x01);
}

uint8_t parallel_read (uint8_t port)
{
    parallel_select(port);
    PARALLEL_DIRECTION &= 0xFFFF0000; // Input
    PDIR_INPUT;
    // Wait for stabilization
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    asm volatile("nop");
    return (uint8_t) PARALLEL_VALUE_INPUT;
}

void parallel_write (uint8_t port, uint8_t value)
{
    parallel_select(port);
    PDIR_OUTPUT;
    PARALLEL_DIRECTION = (PARALLEL_DIRECTION & 0xFFFF0000) + 0x5555; // Input
    PARALLEL_VALUE_OUTPUT = value;
    parallel_select(port+1);
}

void module_select (uint8_t board)
{
    GPIO_WriteBit(GPIOE, GPIO_Pin_7, (board >> 0) & 0x01);
    GPIO_WriteBit(GPIOE, GPIO_Pin_8, (board >> 1) & 0x01);
}

uint8_t module_int_byte (void)
{
    return parallel_read(PORTS_INT_ADDR);
}

// Synchronous pin Input (AD's) and Output (DA's)

void pulse_syn_output (void)
{
    GPIO_ToggleBits(GPIOB, GPIO_Pin_15);
    GPIO_ToggleBits(GPIOB, GPIO_Pin_15);
}

void pulse_syn_input (void)
{
    GPIO_ToggleBits(GPIOB, GPIO_Pin_14);
    GPIO_ToggleBits(GPIOB, GPIO_Pin_14);
}

void debug1_set (void)
{
    GPIO_SetBits(GPIOE, GPIO_Pin_5);
}

void debug1_clr (void)
{
    GPIO_ResetBits(GPIOE, GPIO_Pin_5);
}

void debug2_set (void)
{
    GPIO_SetBits(GPIOE, GPIO_Pin_6);
}

void debug2_clr (void)
{
    GPIO_ResetBits(GPIOE, GPIO_Pin_6);
}
