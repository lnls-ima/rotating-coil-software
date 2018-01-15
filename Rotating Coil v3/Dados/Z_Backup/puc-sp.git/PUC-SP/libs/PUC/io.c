/*
 * This module handles the communication using the SPI for the attached boards.
 */

#include "common.h"
#include "io.h"

#include <stdlib.h>

static const SPI_InitTypeDef IO_SPI_INIT = {
    .SPI_Direction          = SPI_Direction_2Lines_FullDuplex,
    .SPI_Mode               = SPI_Mode_Master,
    .SPI_DataSize           = SPI_DataSize_8b,
    .SPI_CPOL               = SPI_CPOL_Low,
    .SPI_CPHA               = SPI_CPHA_2Edge,
    .SPI_NSS                = SPI_NSS_Soft | SPI_NSSInternalSoft_Set,
    .SPI_BaudRatePrescaler  = SPI_IO_CLK_DIV,
    .SPI_FirstBit           = SPI_FirstBit_MSB,
};

void io_init (void)
{
    SPI_Init(IO_SPI, (SPI_InitTypeDef*) &IO_SPI_INIT);
    SPI_Cmd(IO_SPI, ENABLE);
}
