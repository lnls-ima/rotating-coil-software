#include "spi.h"

inline uint8_t spi_read (SPI_TypeDef* channel)
{
    while( channel->SR & SPI_I2S_FLAG_BSY );
    SPI_I2S_ReceiveData(channel);                   // Clear RX buffer

    while( !(channel->SR & SPI_I2S_FLAG_TXE) );
    SPI_I2S_SendData(channel, 0);                   // Send 0 (generate clk)

    while( !(channel->SR & SPI_I2S_FLAG_RXNE) );
    return SPI_I2S_ReceiveData(channel);            // Read RX Buffer
}

inline void spi_write(SPI_TypeDef* channel, uint8_t data)
{
    while( !(channel->SR & SPI_I2S_FLAG_TXE) ); // Wait tx empty
    SPI_I2S_SendData(channel, data);
}

void spi_read_array (SPI_TypeDef* channel, uint8_t *data, uint32_t count)
{
    while( channel->SR & SPI_I2S_FLAG_BSY );
    SPI_I2S_ReceiveData(channel);                   // Clear RX buffer

    while(count--)
    {
        while( !(channel->SR & SPI_I2S_FLAG_TXE) );
        SPI_I2S_SendData(channel, 0);               // Send 0 (generate clk)

        while( !(channel->SR & SPI_I2S_FLAG_RXNE) );
        *(data++) = SPI_I2S_ReceiveData(channel);   // Read RX Buffer
    }
}

void spi_write_array (SPI_TypeDef* channel, uint8_t *data, uint32_t count)
{
    while(count--)
        spi_write(channel, *(data++));
}

inline void spi_wait(SPI_TypeDef* channel)
{
    while( channel->SR & SPI_I2S_FLAG_BSY );        // Wait SPI BUSY
}

void spi_write_word (SPI_TypeDef* channel, uint32_t data)
{
    spi_write(channel, data >> 24);
    spi_write(channel, data >> 16);
    spi_write(channel, data >>  8);
    spi_write(channel, data);
}

