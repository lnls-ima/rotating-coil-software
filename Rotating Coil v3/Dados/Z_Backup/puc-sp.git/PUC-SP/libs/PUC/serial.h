#ifndef PUC_SERIAL_H
#define PUC_SERIAL_H

#include <server.h>

void serial_init (bsmp_server_t *server);
void uart_init (void);
void config_tim4_int4(void);
void serial_write(void);

#endif

