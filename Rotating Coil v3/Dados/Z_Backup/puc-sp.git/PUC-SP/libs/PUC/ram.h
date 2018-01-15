#ifndef PUC_RAM_H
#define PUC_RAM_H

#include <stdint.h>

#define RAM_CAPACITY        (128*1024)  // 128 KB

void    ram_init            (void);
void    ram_clear           (void);

void    ram_read            (uint32_t address, uint8_t *data, uint32_t len);
void    ram_write           (uint32_t address, uint8_t *data, uint32_t len);

void    ram_stream_start    (uint32_t address);
void    ram_stream_write    (uint8_t value);
void    ram_stream_end      (void);

#endif

