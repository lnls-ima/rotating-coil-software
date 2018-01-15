/*
 * This module contains functions to write to and read from the RAM chip. Read
 * the datasheet of the chip (23LCV1024) for further information.
 */

#include "ram.h"
#include "common.h"
#include "spi.h"

#include <stdbool.h>

enum ram_cmd_code
{
    RAM_CMD_WRITE = 0x02,
    RAM_CMD_READ  = 0x03
};

static inline void ram_select (bool select)
{
    spi_wait(RAM_SPI);
    GPIO_WriteBit(GPIOB, GPIO_Pin_9, !select);
}

static const SPI_InitTypeDef RAM_SPI_INIT = {
    .SPI_Direction           = SPI_Direction_2Lines_FullDuplex,
    .SPI_Mode                = SPI_Mode_Master,
    .SPI_DataSize            = SPI_DataSize_8b,
    .SPI_CPOL                = SPI_CPOL_High,
    .SPI_CPHA                = SPI_CPHA_2Edge,
    .SPI_NSS                 = SPI_NSS_Soft | SPI_NSSInternalSoft_Set,
    .SPI_BaudRatePrescaler   = SPI_RAM_CLK_DIV,
    .SPI_FirstBit            = SPI_FirstBit_MSB,
};

void ram_init (void)
{
    // Configure FLASH SPI
    SPI_Init(RAM_SPI, (SPI_InitTypeDef*) &RAM_SPI_INIT);
    SPI_Cmd (RAM_SPI, ENABLE);

    ram_select(false);
}

void ram_write (uint32_t address, uint8_t *data, uint32_t len)
{
    if(len > RAM_CAPACITY)
        len = RAM_CAPACITY;

    ram_select(true);
    spi_write_word(RAM_SPI, RAM_CMD_WRITE << 24 | address);
    spi_write_array(RAM_SPI, data, len);
    ram_select(false);
}

void ram_read (uint32_t address, uint8_t *data, uint32_t len)
{
    if(len > RAM_CAPACITY)
        len = RAM_CAPACITY;

    ram_select(true);
    spi_write_word(RAM_SPI, RAM_CMD_READ << 24 | address);
    spi_read_array(RAM_SPI, data, len);
    ram_select(false);
}

void ram_clear (void)
{
    ram_select(true);
    spi_write_word(RAM_SPI, RAM_CMD_WRITE << 24);

    unsigned int i;
    for(i = 0; i < RAM_CAPACITY; ++i)
        spi_write(RAM_SPI, 0);

    ram_select(false);
}

void ram_stream_start (uint32_t address)
{
    ram_select(true);
    spi_write_word(RAM_SPI, RAM_CMD_WRITE << 24 | address);
}

void ram_stream_write  (uint8_t value)
{
    spi_write(RAM_SPI, value);
}

void ram_stream_end (void)
{
    ram_select(false);
}
