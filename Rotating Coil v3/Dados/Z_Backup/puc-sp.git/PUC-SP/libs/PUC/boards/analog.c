#include <stdlib.h>

#include "../ports.h"
#include "../boards.h"
#include "../io.h"

#define ANALOG_DATA_SIZE    3
#define ADC_TIMEOUT         10000

// Helper routine to get the number of AD's and DA's indicated by the subtype
static inline void __attribute__ ((always_inline))
break_subtype (uint8_t subtype, unsigned int *n_inp, unsigned int *n_outp)
{
    unsigned int lut[] = {0,1,2,4};
    *n_inp  =  lut[(subtype >> 2) & 0x03];
    *n_outp =  lut[subtype & 0x03];
}

// R/W functions
static void analog_read     (struct var *var);
static void analog_write    (struct var *var);
static bool analog_write_ok (struct bsmp_var *var, uint8_t *value);

// Direct hardware manipulation functions
static void dac_init  (struct var *var);

// Initialize the analog board
void analog_init (struct board *b)
{
    unsigned int n_inp, n_outp, n_ios;

    break_subtype(b->subtype, &n_inp, &n_outp);
    n_ios = n_inp + n_outp;

    unsigned int i;
    for(i = 0; i < n_ios; ++i)
    {
        bool is_input = i < n_inp;
        struct var *v = boards_get_var_slot(ANALOG_DATA_SIZE);
        v->address            = i;
        v->board              = b;
        v->read_synch         = true;
        v->write_synch        = true;
        v->read               = is_input ? analog_read : NULL;
        v->write              = is_input ? NULL : analog_write;
        v->type               = is_input ? VAR_ANALOG_INPUT : VAR_ANALOG_OUTPUT;
        v->svar.value_ok      = is_input ? NULL : analog_write_ok;
        v->svar.info.writable = is_input ? false : true;

        if(!is_input)
            dac_init(v);
    }
}

static void analog_read (struct var *var)
{
    module_select(var->board->address);

    uint32_t adc_data;
    uint8_t *data = var->svar.data;

    chip_select(var->address);

    // Wait conversion
    unsigned int timeout = ADC_TIMEOUT;
    while(!(module_int_byte() & (1u << var->address)) && timeout--);

    adc_data  = (io_read() << 10);
    adc_data |= (io_read() <<  2);
    adc_data |= (io_read() >>  6);

    chip_select(var->address + 1);

    // Write to the appropriate bytes
    data[0] = adc_data >> 16;
    data[1] = adc_data >> 8;
    data[2] = adc_data;

    module_select(var->board->address + 1);
}

static void analog_write (struct var *var)
{
    module_select(var->board->address);

    uint8_t *data  = var->svar.data;
    uint32_t value = (data[0] << 16) + (data[1] << 8) + data[2];
    uint32_t cmd   = 0x100000 | (value << 2);

    chip_select(var->address);
    io_write(cmd >> 16);
    io_write(cmd >> 8);
    io_write(cmd);
    io_wait();
    chip_select(var->address + 1);

    module_select(var->board->address + 1);
}

static void dac_init (struct var *var)
{
    chip_select(var->address);
    io_write(0x20);
    io_write(0x03);
    io_write(0x10);         // Old reference
    //io_write(0x12);         // New reference
    io_wait();
    chip_select(var->address + 1);

    var->svar.data[0] = 0x02;
    var->svar.data[1] = 0x00;
    var->svar.data[2] = 0x00;

    analog_write(var);

    pulse_syn_output();
}

// Check value
static bool analog_write_ok (struct bsmp_var *var, uint8_t *value)
{
    (void)var;
    return value[0] <= 3;   // Values greater than 3 indicate more than 18-bits
}

