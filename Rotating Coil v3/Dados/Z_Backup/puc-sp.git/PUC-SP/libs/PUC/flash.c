/*
 * This module contains functions to write to and read from the Flash chip. Read
 * the datasheet of the chip (W25Q64FV) for further information.
 */

#include "flash.h"
#include "common.h"
#include "spi.h"

#include <stdint.h>
#include <stdbool.h>

enum flash_cmd_code
{
    FLASH_CMD_WRITE                 = 0x02,
    FLASH_CMD_READ                  = 0x03,
    FLASH_CMD_READ_STATUS           = 0x05,
    FLASH_CMD_WRITE_ENABLE          = 0x06,
    FLASH_CMD_ERASE_SECTOR          = 0x20,
    FLASH_CMD_ERASE_32K_BLOCK       = 0x52,
    FLASH_CMD_ERASE_64K_BLOCK       = 0xD8,
    FLASH_CMD_ERASE_CHIP            = 0x60,
    FLASH_CMD_POWER_DOWN            = 0xB9,
    FLASH_CMD_RELEASE_POWER_DOWN    = 0xAB,
};

#define FLASH_IS_BUSY_MASK          0x01            // Least significant bit
#define FLASH_PAGE_SIZE             256             // 256 bytes

#define FLASH_PAGES_PER_SECTOR      (FLASH_SECTOR_SIZE/FLASH_PAGE_SIZE)
#define FLASH_SECTORS               (FLASH_CAPACITY/FLASH_SECTOR_SIZE)

static const SPI_InitTypeDef FLASH_SPI_INIT = {
    .SPI_Direction          = SPI_Direction_2Lines_FullDuplex,
    .SPI_Mode               = SPI_Mode_Master,
    .SPI_DataSize           = SPI_DataSize_8b,
    .SPI_CPOL               = SPI_CPOL_High,
    .SPI_CPHA               = SPI_CPHA_2Edge,
    .SPI_NSS                = SPI_NSS_Soft | SPI_NSSInternalSoft_Set,
    .SPI_BaudRatePrescaler  = SPI_FLASH_CLK_DIV,
    .SPI_FirstBit           = SPI_FirstBit_MSB,
};

static inline uint32_t min (uint32_t a, uint32_t b)
{
    return a < b ? a : b;
}

static inline void flash_select (bool select)
{
    spi_wait(FLASH_SPI);
    GPIO_WriteBit(GPIOA, GPIO_Pin_4, !select);
}

void flash_init (void)
{
    SPI_Init(FLASH_SPI, (SPI_InitTypeDef*) &FLASH_SPI_INIT);
    SPI_Cmd (FLASH_SPI, ENABLE);

    flash_select(false);

    flash_select(true);
    spi_write(FLASH_SPI, 0xAA);
    flash_select(false);
}

static inline uint8_t flash_command_rb (enum flash_cmd_code command)// Read Back
{
    uint8_t val = 0;
    flash_select(true);
    spi_write(FLASH_SPI, command);
    val = spi_read(FLASH_SPI);
    flash_select(false);
    return val;
}

static inline void flash_command (enum flash_cmd_code command)
{
    flash_select(true);
    spi_write(FLASH_SPI, command);
    flash_select(false);
}

static inline void flash_wait(void)
{
    while(flash_command_rb(FLASH_CMD_READ_STATUS) & FLASH_IS_BUSY_MASK);
}

void flash_sector_write (uint16_t sector, uint8_t *data, uint32_t len)
{
    if(sector >= FLASH_SECTORS)
        return;

    if(len > FLASH_SECTOR_SIZE)
        len = FLASH_SECTOR_SIZE;

    uint32_t address = sector*FLASH_SECTOR_SIZE;
    
    // Erase
    flash_command (FLASH_CMD_WRITE_ENABLE);

    flash_select(true);
    spi_write_word(FLASH_SPI, (FLASH_CMD_ERASE_SECTOR << 24) | address);
    flash_select(false);

    flash_wait();

    uint32_t written = 0;

    while(written < len)
    {
        flash_command (FLASH_CMD_WRITE_ENABLE);

        flash_select(true);
        spi_write_word(FLASH_SPI, (FLASH_CMD_WRITE << 24) | address);
        spi_write_array(FLASH_SPI, data, min(len - written, FLASH_PAGE_SIZE));
        flash_select(false);

        address += FLASH_PAGE_SIZE;
        data    += FLASH_PAGE_SIZE;
        written += FLASH_PAGE_SIZE;

        flash_wait();
    }
}

void flash_read (uint32_t address, uint8_t *data, uint32_t len)
{
    flash_wait();

    flash_select(true);
    spi_write_word(FLASH_SPI, (FLASH_CMD_READ << 24) | address);
    spi_read_array(FLASH_SPI, data, len);
    flash_select(false);
}

void flash_stream_start (uint32_t address)
{
    flash_wait();
    flash_select(true);
    spi_write_word(FLASH_SPI, (FLASH_CMD_READ << 24) | address);
}

uint8_t flash_stream_read (void)
{
    return spi_read(FLASH_SPI);
}

inline void flash_stream_end (void)
{
    flash_select(false);
}
