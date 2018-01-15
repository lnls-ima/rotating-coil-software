#ifndef PUC_PORTS_H
#define PUC_PORTS_H

#include <stdint.h>
#include <stdbool.h>
#include "stm32f4xx.h"


void ports_init (void);
void uart_enable (bool enable);
uint8_t get_serial_address (void);
void chip_select(uint8_t chip);

// Parallel direction
//#define PDIR_OUTPUT             1
//#define PDIR_INPUT              0
#define PDIR_OUTPUT             GPIO_WriteBit(GPIOB, GPIO_Pin_6, 1)
#define PDIR_INPUT              GPIO_WriteBit(GPIOB, GPIO_Pin_6, 0) //B6

// Parallel value
#define PARALLEL_DIRECTION      GPIOD->MODER //TRISE - > D0 a D7
#define PARALLEL_VALUE_OUTPUT   GPIOD->ODR
#define PARALLEL_VALUE_INPUT	 GPIOD->IDR

void parallel_select (uint8_t parallel);
uint8_t parallel_read (uint8_t port);
void parallel_write (uint8_t port, uint8_t value);
void module_select (uint8_t board);

// Board manipulation

#define PORTS_DESC_ADDR         0x07    // Board description byte address
#define PORTS_DESC_EXTENDED     0x05    // Next board description byte address
#define PORTS_INT_ADDR          0x06    // Board interrupt byte address
#define PORTS_DESC_NO_BOARD     0xFF    // Board description if there's no
                                        // board at the current address
#define PORTS_DESC_READ_NEXT    0xFE    // Read the next description address

uint8_t module_int_byte (void);

// Synchronous pin Input (AD's) and Output (DA's)

void pulse_syn_output (void);
void pulse_syn_input (void);

void debug1_set (void);
void debug1_clr (void);
void debug2_set (void);
void debug2_clr (void);

#endif

