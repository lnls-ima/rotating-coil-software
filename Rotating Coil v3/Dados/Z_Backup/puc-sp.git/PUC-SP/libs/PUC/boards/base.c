#include "common.h"
#include "../ram.h"
#include "../flash.h"
#include "../sync.h"
#include "../boards.h"

#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define BASE_CURVE_BLOCK_SIZE       4096
#define BASE_CURVE_NBLOCKS          32      // 128k curves
#define VAR_DETECTED_BOARDS_SIZE    4
#define VAR_SYNC_STATE_SIZE         4
#define VAR_SYNC_CONFIG_SIZE        6

// Vars
static void base_get_sync_state     (struct var *v);
static void base_get_sync_config    (struct var *v);
static void base_set_sync_config    (struct var *v);
static bool base_check_sync_config  (struct bsmp_var *var, uint8_t *value);

// Curves
static void base_curve_read         (struct bsmp_curve *curve, uint16_t block,
                                     uint8_t *data, uint16_t *len);
static void base_curve_write        (struct bsmp_curve *curve, uint16_t block,
                                     uint8_t *data, uint16_t len);

// Functions
static uint8_t base_func_sync_start     (uint8_t *in, uint8_t *out);
static uint8_t base_func_sync_stop      (uint8_t *in, uint8_t *out);
static uint8_t base_func_sync_pause     (uint8_t *in, uint8_t *out);
static uint8_t base_func_sync_step      (uint8_t *in, uint8_t *out);
static uint8_t base_func_reset          (uint8_t *in, uint8_t *out);

void base_init (struct board *b)
{
    unsigned int i;

    struct var *v;

    v = boards_get_var_slot(VAR_DETECTED_BOARDS_SIZE);
    v->address              = 0;
    v->type                 = VAR_BASE_DETECTED_BOARDS;
    v->board                = b;
    v->read_synch           = false;
    v->write_synch          = false;
    v->read                 = NULL;
    v->write                = NULL;
    v->svar.value_ok        = NULL;
    v->svar.info.writable   = false;

    v = boards_get_var_slot(VAR_SYNC_STATE_SIZE);
    v->address              = 1;
    v->type                 = VAR_BASE_SYNC_STATE;
    v->board                = b;
    v->read_synch           = false;
    v->write_synch          = false;
    v->read                 = base_get_sync_state;
    v->write                = NULL;
    v->svar.value_ok        = NULL;
    v->svar.info.writable   = false;

    v = boards_get_var_slot(VAR_SYNC_CONFIG_SIZE);
    v->address              = 2;
    v->type                 = VAR_BASE_SYNC_CONFIG;
    v->board                = b;
    v->read_synch           = false;
    v->write_synch          = false;
    v->read                 = base_get_sync_config;
    v->write                = base_set_sync_config;
    v->svar.value_ok        = base_check_sync_config;
    v->svar.info.writable   = true;

    // Curves

    for(i = CURVE_BASE_RAM; i <= CURVE_BASE_FLASH; ++i)
    {
        struct curve *c = boards_get_curve_slot();
        c->board                  = b;
        c->first_block            = 0;
        c->type                   = i;
        c->scurve.read_block      = base_curve_read;
        c->scurve.write_block     = base_curve_write;
        c->scurve.info.block_size = BASE_CURVE_BLOCK_SIZE;
        c->scurve.info.nblocks    = BASE_CURVE_NBLOCKS;
        c->scurve.info.writable   = i == CURVE_BASE_FLASH;
    }

    // Functions

    bsmp_func_t base_funcs[] = {
        base_func_reset, base_func_sync_start, base_func_sync_stop,
        base_func_sync_pause, base_func_sync_step,
    };

    for(i = FUNC_BASE_RESET; i <= FUNC_BASE_SYNC_STEP; ++i)
    {
        struct func *f = boards_get_func_slot();
        f->board = b;
        f->type  = i;
        f->sfunc.info.input_size = 0;
        f->sfunc.info.output_size = 0;
        f->sfunc.func_p = base_funcs[i - FUNC_BASE_RESET];
    }
}

static void base_get_sync_state (struct var *v)
{
    uint32_t index = sync_get_index();
    v->svar.data[0] = sync_get_state() << 6;
    v->svar.data[1] = index >> 16;
    v->svar.data[2] = index >> 8;
    v->svar.data[3] = index;
}

static void base_get_sync_config (struct var *v)
{
    sync_get_config((struct sync_config *)v->svar.data);
}

static void base_set_sync_config (struct var *v)
{
    sync_set_config((struct sync_config *)v->svar.data);
}


static bool base_check_sync_config  (struct bsmp_var *var, uint8_t *value)
{
    (void)var;
    return sync_check_config((struct sync_config *)value) == SYNC_OK;
}

static void base_curve_read (struct bsmp_curve *curve, uint16_t block,
                             uint8_t *data, uint16_t *len)
{
    *len = 0;

    if(block >= BASE_CURVE_NBLOCKS)
        return;

    /*if(sync_get_state() == SYNC_RUNNING)
    {
        *len = 0;
        return;
    }*/

    struct curve *c = (struct curve *) curve->user;
    uint32_t address = (c->first_block + block)*BASE_CURVE_BLOCK_SIZE;

    *len = BASE_CURVE_BLOCK_SIZE;
    if(c->type == CURVE_BASE_FLASH)
        flash_read (address, data, *len);
    else
        ram_read (address, data, *len);
}

static void base_curve_write (struct bsmp_curve *curve, uint16_t block,
                               uint8_t *data, uint16_t len)
{
    struct curve *c = (struct curve *) curve->user;
    flash_sector_write(c->first_block + block, data, len);
}

enum sync_state_err
{
    SYNC_STATE_OK,
    SYNC_STATE_ALREADY_RUNNING,
    SYNC_STATE_ALREADY_PAUSED,
    SYNC_STATE_ALREADY_STOPPED,
    SYNC_STATE_ARGS_INVALID,
    SYNC_STATE_NOT_RUNNING,
};

static uint8_t base_func_sync_start (uint8_t *inp, uint8_t *outp)
{
    (void)inp, (void)outp; // unused

    enum sync_err sync_err = sync_start();

    if(sync_err == SYNC_ERR_RUNNING)
        return SYNC_STATE_ALREADY_RUNNING;
    else if(sync_err == SYNC_ERR_NOTHING_TO_DO)
        return SYNC_STATE_ARGS_INVALID;
    return SYNC_STATE_OK;
}

static uint8_t base_func_sync_stop (uint8_t *in, uint8_t *out)
{
    (void)in,(void)out; // unused

    enum sync_state_err err   = SYNC_STATE_OK;
    enum sync_state     state = sync_get_state();

    if(state == SYNC_RUNNING || state == SYNC_PAUSED)
        sync_stop();
    else
        err = SYNC_STATE_ALREADY_STOPPED;

    return err;
}

static uint8_t base_func_sync_pause (uint8_t *in, uint8_t *out)
{
    (void)in,(void)out; // unused

    enum sync_state_err err   = SYNC_STATE_OK;
    enum sync_state     state = sync_get_state();

    if(state == SYNC_PAUSED)
        err = SYNC_STATE_ALREADY_PAUSED;
    else if(state == SYNC_STOPPED)
        err = SYNC_STATE_ALREADY_STOPPED;
    else
        sync_pause();

    return err;
}

static uint8_t base_func_sync_step (uint8_t *in, uint8_t *out)
{
    (void)in,(void)out; // unused

    if(sync_get_state() != SYNC_RUNNING)
        return SYNC_STATE_NOT_RUNNING;

    sync_step();
    return SYNC_STATE_OK;
}

static uint8_t base_func_reset (uint8_t *in, uint8_t *out)
{
    (void)in,(void)out; // unused
    NVIC_SystemReset();
    return 0;
}
