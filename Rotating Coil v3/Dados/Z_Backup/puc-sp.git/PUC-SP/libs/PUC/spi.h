#ifndef PUC_SPI_H
#define PUC_SPI_H

#include <stdint.h>
#include <stdbool.h>
#include <stm32f4xx.h>

uint8_t spi_read  (SPI_TypeDef* channel);
void    spi_write (SPI_TypeDef* channel, uint8_t data);
void    spi_wait  (SPI_TypeDef* channel);

void spi_write_word  (SPI_TypeDef* channel, uint32_t data);
void spi_read_array  (SPI_TypeDef* channel, uint8_t *data, uint32_t count);
void spi_write_array (SPI_TypeDef* channel, uint8_t *data, uint32_t count);

#endif
