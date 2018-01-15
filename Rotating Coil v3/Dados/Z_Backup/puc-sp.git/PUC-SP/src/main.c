#include "stm32f4xx.h"
#include "bsmp.h"

//Includes PIC:
#include "io.h"
#include "ports.h"
#include "common.h"
#include "flash.h"
#include "ram.h"
#include "boards.h"
#include "serial.h"
#include "sync.h"

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <server.h>

#define VECT_TAB_OFFSET             0x20000

static bsmp_server_t bsmp;

void ligaClocks()
{
      /* Periph clock enable */
      RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOA, ENABLE);
      RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOB, ENABLE);
      RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOC, ENABLE);
      RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOD, ENABLE);
      RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOE, ENABLE);
      RCC_APB2PeriphClockCmd(RCC_APB2Periph_SYSCFG, ENABLE);
      RCC_APB2PeriphClockCmd(RCC_APB2Periph_SPI4, ENABLE);
      RCC_APB1PeriphClockCmd(RCC_APB1Periph_SPI2, ENABLE);
      RCC_APB2PeriphClockCmd(RCC_APB2Periph_SPI1, ENABLE);
      RCC_APB2PeriphClockCmd(RCC_APB2Periph_USART1, ENABLE);
      RCC_APB1PeriphClockCmd(RCC_APB1Periph_TIM2, ENABLE);
      RCC_APB1PeriphClockCmd(RCC_APB1Periph_TIM3, ENABLE);
      RCC_APB1PeriphClockCmd(RCC_APB1Periph_TIM4, ENABLE);
      RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_DMA2, ENABLE);
}

int main(void)
{
    __enable_irq();

    NVIC_SetVectorTable(NVIC_VectTab_FLASH, VECT_TAB_OFFSET);
    NVIC_PriorityGroupConfig(NVIC_PriorityGroup_3);

    ligaClocks();

    // Initialize Communications Library
    bsmp_server_init(&bsmp);

    // Set the hook function of the library
    bsmp_register_hook(&bsmp, boards_hook);

    // Initialize basic program modules
    ports_init();
    flash_init();
    ram_init();
    io_init();

    // Initialize all boards
    boards_init(&bsmp);

    // Initialize interrupt-driven modules
    sync_init();
    serial_init(&bsmp);

    for(;;)         // Sleep mode. Down from 483 mA to 452 mA of comsumption
        __WFI();    // WFI = Wait For Interrupt

    return EXIT_SUCCESS;
}

