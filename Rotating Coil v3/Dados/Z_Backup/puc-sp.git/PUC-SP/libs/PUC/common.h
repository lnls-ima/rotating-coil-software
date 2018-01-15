#ifndef PUC_COMMON_H
#define PUC_COMMON_H

#include <stm32f4xx.h>

#define FREQ_180M_BAUD_8M

// Maximum ratings for the SPI
// CPU:       SYS_FREQ/2 MHz
// Flash (8 Mbytes): 104 MHz
// RAM (128 kbytes):  20 MHz
// A/D:               17 MHz
// D/A:               25 MHz

#if defined(FREQ_180M_BAUD_8M)
#define SYS_FREQ                180000000
#define UART_BAUD               6000000
#define UART_TIMER_PRESCALER    45000       // 180M/45k = 4kHz: 4 ticks per ms
#define UART_TIMER_PERIOD_MS    200         // 200 ms of timeout (800 ticks)
#define UART_TIMER_TICKS_PER_MS (SYS_FREQ/UART_TIMER_PRESCALER/1000)
#define UART_TIMER_PERIOD       (UART_TIMER_TICKS_PER_MS*UART_TIMER_PERIOD_MS)

#define SPI_FLASH_CLK_DIV       SPI_BaudRatePrescaler_2     // 45 MHz
#define SPI_RAM_CLK_DIV         SPI_BaudRatePrescaler_4     // 22.5 MHz
#define SPI_IO_CLK_DIV          SPI_BaudRatePrescaler_4     // 22.5 MHz
#else
#error "Configure a frequency by uncommenting one in common.h"
#endif

// Peripherals for different modules
#define FLASH_SPI               SPI1
#define RAM_SPI                 SPI2
#define IO_SPI                  SPI4

#define SERIAL_DMA_RX           DMA2_Stream2
#define SERIAL_DMA_RX_IRQn      DMA2_Stream2_IRQn
#define SERIAL_DMA_RX_IRQ       void  DMA2_Stream2_IRQHandler (void)
#define SERIAL_DMA_RX_CHN       DMA_Channel_4
#define SERIAL_DMA_RX_IF        DMA_IT_TCIF2
#define SERIAL_DMA_RX_PRIO      6
#define SERIAL_DMA_RX_SUB_PRIO  1

#define SERIAL_DMA_TX           DMA2_Stream7
#define SERIAL_DMA_TX_IRQn      DMA2_Stream7_IRQn
#define SERIAL_DMA_TX_IRQ       void DMA2_Stream7_IRQHandler (void)
#define SERIAL_DMA_TX_CHN       DMA_Channel_4
#define SERIAL_DMA_TX_IF        DMA_IT_TCIF7
#define SERIAL_DMA_TX_PRIO      6
#define SERIAL_DMA_TX_SUB_PRIO  0

#define SERIAL_TIMER            TIM4            // 16-bit general purpose timer
#define SERIAL_TIMER_IRQn       TIM4_IRQn
#define SERIAL_TIMER_IRQ        void TIM4_IRQHandler (void)
#define SERIAL_TIMER_PRIO       5
#define SERIAL_TIMER_SUB_PRIO   0

#define SERIAL_UART             USART1
#define SERIAL_UART_IRQn        USART1_IRQn
#define SERIAL_UART_IRQ         void USART1_IRQHandler (void)
#define SERIAL_UART_IF          USART_IT_ERR
#define SERIAL_UART_PRIO        7
#define SERIAL_UART_SUB_PRIO    0

#define SYNC_TIMER              TIM3
#define SYNC_TIMER_PRESCALER    3000    // 180M/3k = 60kHz
#define SYNC_TIMER_IRQn         TIM3_IRQn
#define SYNC_TIMER_IRQ          void TIM3_IRQHandler (void)
#define SYNC_TIMER_PRIO         7
#define SYNC_TIMER_SUB_PRIO     0

#define SYNC_EXTI               EXTI_Line10
#define SYNC_EXTI_PORT          EXTI_PortSourceGPIOD
#define SYNC_EXTI_PIN           EXTI_PinSource10
#define SYNC_EXTI_IRQn          EXTI15_10_IRQn
#define SYNC_EXTI_IRQ           void EXTI15_10_IRQHandler (void)
#define SYNC_EXTI_PRIO          7
#define SYNC_EXTI_SUB_PRIO      0

#include <stdbool.h>
#include <server.h>

#endif

