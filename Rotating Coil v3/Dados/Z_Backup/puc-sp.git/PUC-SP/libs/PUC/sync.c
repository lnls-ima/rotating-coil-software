/*
 * This module contains a function that, when enabled, reads a point from the
 * Flash and writes that point to a D/A converter when an external interrupt is
 * received.
 */

#include "sync.h"
#include "common.h"
#include "ports.h"
#include "io.h"
#include "flash.h"
#include "ram.h"
#include "boards.h"

#include <stdlib.h>
#include <string.h>

#define SYNC_POINT_SIZE         2
#define SYNC_WPOINT_SIZE        4
#define SYNC_MIN_DIVISOR        1
#define SYNC_MAX_DIVISOR        65535
#define SYNC_MAX_POINTS         65536
#define SYNC_MAX_WPOINTS        32768
#define SYNC_MAX_CLK_BIT        7
#define SYNC_ANALOG_VAR_SIZE    3
#define SYNC_DIGITAL_VAR_SIZE   1
#define SYNC_18_BIT_MASK        0x3FFFF

#define TO16(d)                 (((d)[0] << 8) | (d)[1])

static struct
{
    uint32_t index;
    uint32_t npoints;
    uint32_t point_size;
    uint32_t locked_resources;

    struct var *ad;
    struct var *da;
    struct var *digout;

    enum sync_state     state;
    struct sync_config  config;
} sync_state = {
    .state = SYNC_STOPPED,
    .point_size = SYNC_POINT_SIZE,
};

static const NVIC_InitTypeDef TIMER_NVIC_INIT = {
    .NVIC_IRQChannel                    = SYNC_TIMER_IRQn,
    .NVIC_IRQChannelPreemptionPriority  = SYNC_TIMER_PRIO,
    .NVIC_IRQChannelSubPriority         = SYNC_TIMER_SUB_PRIO,
    .NVIC_IRQChannelCmd                 = ENABLE,
};

static const NVIC_InitTypeDef EXTI_NVIC_INIT = {
    .NVIC_IRQChannel                    = SYNC_EXTI_IRQn,
    .NVIC_IRQChannelPreemptionPriority  = SYNC_EXTI_PRIO,
    .NVIC_IRQChannelSubPriority         = SYNC_EXTI_SUB_PRIO,
    .NVIC_IRQChannelCmd                 = DISABLE,
};

static const EXTI_InitTypeDef EXTI_INIT = {
    .EXTI_Line      = SYNC_EXTI,
    .EXTI_Mode      = EXTI_Mode_Interrupt,
    .EXTI_Trigger   = EXTI_Trigger_Rising,
    .EXTI_LineCmd   = ENABLE,
};

void sync_init (void)
{
    // Initialize timer interrupt
    NVIC_Init((NVIC_InitTypeDef*) &TIMER_NVIC_INIT);
    TIM_ITConfig(SYNC_TIMER, TIM_IT_Update, ENABLE);

    // Initialize external interrupt
    SYSCFG_EXTILineConfig(SYNC_EXTI_PORT, SYNC_EXTI_PIN);
    NVIC_Init((NVIC_InitTypeDef*) &EXTI_NVIC_INIT);
    EXTI_Init((EXTI_InitTypeDef*) &EXTI_INIT);

    sync_state.ad     = boards_get_first_var(VAR_ANALOG_INPUT);
    sync_state.da     = boards_get_first_var(VAR_ANALOG_OUTPUT);
    sync_state.digout = boards_get_first_var(VAR_DIGITAL_OUTPUT);
}

enum sync_state sync_get_state (void)
{
    return sync_state.state;
}

uint32_t sync_get_index (void)
{
    return sync_state.index;
}

enum sync_err sync_check_config (struct sync_config *cfg)
{
    // Sync MUST be stopped to perform any change
    if(sync_state.state != SYNC_STOPPED)
        return SYNC_ERR_RUNNING;

    // There must be an analog board present to perform analog I/O
    if(!sync_state.ad && cfg->in_enabled)
        return SYNC_ERR_INVALID_CFG;

    if(!sync_state.da && cfg->out_enabled)
        return SYNC_ERR_INVALID_CFG;

    // There must be a digital board present to perform digital output
    if(!sync_state.digout && (cfg->clk_out_en || cfg->clk_pulse_en))
        return SYNC_ERR_INVALID_CFG;

    // Wide points (18-bit) impose a different limit on npoints
    if(cfg->wide_point && TO16(cfg->npoints) > SYNC_MAX_WPOINTS)
        return SYNC_ERR_INVALID_CFG;

    // Can't accept an invalid clock source
    if(cfg->clk_source == SYNC_CLK_SRC_MAX)
        return SYNC_ERR_INVALID_CFG;

    // Divisor can't be zero
    if(TO16(cfg->clk_divisor) < SYNC_MIN_DIVISOR)
        return SYNC_ERR_INVALID_CFG;

    // There must not be a conflict of output bits
    if(cfg->clk_out_en && cfg->clk_pulse_en)
        if(cfg->clk_out_bit == cfg->clk_pulse_bit)
            return SYNC_ERR_INVALID_CFG;

    return SYNC_OK;
}

void sync_set_config (struct sync_config *cfg)
{
    if(sync_state.state != SYNC_STOPPED)
        return;

    memcpy(&sync_state.config, cfg, sizeof(sync_state.config));

    uint16_t npoints = TO16(cfg->npoints);
    sync_state.npoints = npoints ? npoints : SYNC_MAX_POINTS;
    sync_state.point_size = cfg->wide_point ? SYNC_WPOINT_SIZE:SYNC_POINT_SIZE;
}

void sync_get_config (struct sync_config *cfg)
{
    memcpy(cfg, &sync_state.config, sizeof(*cfg));
}

enum sync_err sync_start  (void)
{
    if(sync_state.state == SYNC_RUNNING)
        return SYNC_ERR_RUNNING;

    // Can only reconfigure at STOPPED state
    if(sync_state.state == SYNC_STOPPED)
    {
        // Check if there's something to do
        struct sync_config *cfg = &sync_state.config;
        if(!(cfg->in_enabled || cfg->out_enabled || cfg->clk_out_en ||
                cfg->clk_pulse_en))
            return SYNC_ERR_NOTHING_TO_DO;

        if(!sync_state.npoints)
            return SYNC_ERR_NOTHING_TO_DO;

        if(cfg->clk_source == SYNC_CLK_INTERNAL)
        {
            // Clock @ 120 kHz: (Period is counter limit)
            //   Divisor = 1  --> steps @ 60 kHz
            //   Divisor = 2  --> steps @ 30 kHz
            //   Divisor = 4  --> steps @ 15 kHz
            //   ...
            TIM_TimeBaseInitTypeDef timerInit = {
                .TIM_Period         = TO16(cfg->clk_divisor),
                .TIM_Prescaler      = SYNC_TIMER_PRESCALER - 1,
                .TIM_ClockDivision  = 0,
                .TIM_CounterMode    = TIM_CounterMode_Up,
            };
            TIM_TimeBaseInit(SYNC_TIMER, &timerInit);
        }

        if(sync_state.config.in_enabled)
        {
            ram_clear();
            ram_stream_start(0);
        }

        if(sync_state.config.out_enabled)
            flash_stream_start(0);

        sync_state.index = 0;
    }

    if(sync_state.config.clk_source == SYNC_CLK_INTERNAL)
        TIM_Cmd(SYNC_TIMER, ENABLE);
    else if(sync_state.config.clk_source == SYNC_CLK_EXTERNAL)
        NVIC_EnableIRQ(SYNC_EXTI_IRQn);

    sync_state.state = SYNC_RUNNING;

    return SYNC_OK;
}

void sync_stop (void)
{
    if(sync_state.state == SYNC_STOPPED)
        return;

    if(sync_state.config.in_enabled)
        ram_stream_end();

    if(sync_state.config.out_enabled)
        flash_stream_end();

    if(sync_state.config.clk_source == SYNC_CLK_INTERNAL)
        TIM_Cmd(SYNC_TIMER, DISABLE);
    else if(sync_state.config.clk_source == SYNC_CLK_EXTERNAL)
        NVIC_DisableIRQ(SYNC_EXTI_IRQn);

    sync_state.state = SYNC_STOPPED;
}

void sync_pause (void)
{
    if(sync_state.state == SYNC_RUNNING)
    {
        sync_state.state = SYNC_PAUSED;

        if(sync_state.config.clk_source == SYNC_CLK_INTERNAL)
            TIM_Cmd(SYNC_TIMER, DISABLE);
    }
}

static inline void pulse_bit (struct var *v, uint8_t bit)
{
    v->svar.data[0] ^= 1 << bit;
    v->write(v);
    v->svar.data[0] ^= 1 << bit;
    v->write(v);
}

void sync_step (void)
{
    // If not running, ignore step
    if(sync_state.state != SYNC_RUNNING)
        return;

    debug2_clr();

    unsigned int i;

    if(sync_state.config.in_enabled)
    {
        // Read from A/D
        pulse_syn_input();
        sync_state.ad->read(sync_state.ad);

        uint32_t point = 0;
        uint8_t *data = sync_state.ad->svar.data;

        point = (data[0] << 16) | (data[1] << 8) | data[2];
        point &= SYNC_18_BIT_MASK;

        // Write to RAM
        if(!sync_state.config.wide_point)
            point >>= 2;        // Make 16-bit out of 18-bit value

        for(i = 0; i < sync_state.point_size; ++i)
            ram_stream_write(point >> (8*(sync_state.point_size-1-i)));
    }

    if(sync_state.config.out_enabled)
    {
        // Read from flash
        uint32_t point = 0;

        for(i = 0; i < sync_state.point_size; ++i)
            point = (point << 8) | flash_stream_read();

        if(!sync_state.config.wide_point)
            point <<= 2;        // Make 18-bit out of 16-bit value

        point &= SYNC_18_BIT_MASK;

        // Write to the D/A
        uint8_t *data = sync_state.da->svar.data;
        data[0] = point >> 16;
        data[1] = point >> 8;
        data[2] = point;

        sync_state.da->write(sync_state.da);
        pulse_syn_output();
    }

    if(sync_state.config.clk_out_en)
        pulse_bit(sync_state.digout, sync_state.config.clk_out_bit);

    ++sync_state.index; // Next point index

    // Check if it is over
    if(sync_state.index == sync_state.npoints)
    {
        if(sync_state.config.clk_pulse_en)
            pulse_bit(sync_state.digout, sync_state.config.clk_pulse_bit);

        sync_stop();
    }
    debug2_set();
}

SYNC_TIMER_IRQ
{
    sync_step();
    TIM_ClearFlag(SYNC_TIMER, TIM_FLAG_Update);
    TIM_ClearITPendingBit(SYNC_TIMER, TIM_IT_Update);
}

SYNC_EXTI_IRQ
{
    sync_step();
    EXTI_ClearFlag(SYNC_EXTI);
    EXTI_ClearITPendingBit(SYNC_EXTI);
}
