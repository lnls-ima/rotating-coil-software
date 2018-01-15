#ifndef PUC_FLASH_H
#define PUC_FLASH_H

#include <stdint.h>

#define  FLASH_CAPACITY         (8*1024*1024)   // 8 MB
#define  FLASH_SECTOR_SIZE      (4*1024)        // 4 KB

void     flash_init             (void);

void     flash_sector_write     (uint16_t sector, uint8_t *data, uint32_t len);
void     flash_read             (uint32_t address, uint8_t *data, uint32_t len);

void     flash_stream_start     (uint32_t address);
uint8_t  flash_stream_read      (void);
void     flash_stream_end       (void);

#endif

