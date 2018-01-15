#ifndef PUC_SYNC_H
#define PUC_SYNC_H

#include <stdbool.h>
#include <stdint.h>

enum sync_state
{
    SYNC_STOPPED,
    SYNC_RUNNING,
    SYNC_PAUSED,
};

enum sync_err
{
    SYNC_OK,
    SYNC_ERR_INVALID_CFG,
    SYNC_ERR_RUNNING,
    SYNC_ERR_NOTHING_TO_DO,
};

enum sync_clk_src
{
    SYNC_CLK_INTERNAL,
    SYNC_CLK_EXTERNAL,
    SYNC_CLK_COMMUNICATION,

    SYNC_CLK_SRC_MAX,
};

struct sync_config
{
    uint8_t : 3;            // least significant bits
    enum sync_clk_src clk_source: 2;
    bool wide_point : 1;
    bool in_enabled : 1;
    bool out_enabled : 1;   // most significant bit

    uint8_t npoints[2];
    uint8_t clk_divisor[2];

    uint8_t clk_pulse_bit : 3;
    bool clk_pulse_en  : 1;
    uint8_t clk_out_bit : 3;
    bool clk_out_en : 1;
}__attribute__((packed));

enum sync_state sync_get_state (void);
uint32_t        sync_get_index (void);

enum sync_err   sync_check_config (struct sync_config *cfg);
void            sync_set_config   (struct sync_config *cfg);
void            sync_get_config   (struct sync_config *cfg);

enum sync_err   sync_start (void);

void sync_init  (void);
void sync_stop  (void);
void sync_pause (void);
void sync_step  (void);

#endif

