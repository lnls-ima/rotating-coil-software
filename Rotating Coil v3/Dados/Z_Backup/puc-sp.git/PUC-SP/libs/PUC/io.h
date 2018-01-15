#ifndef PUC_IO_H
#define PUC_IO_H

#include "common.h"
#include "spi.h"
#include <stdint.h>

void    io_init(void);

#define io_read()   spi_read(IO_SPI)
#define io_write(v) spi_write(IO_SPI, (v))
#define io_wait()   spi_wait(IO_SPI)

#endif

