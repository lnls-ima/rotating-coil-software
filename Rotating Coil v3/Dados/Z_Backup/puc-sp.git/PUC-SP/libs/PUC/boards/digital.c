#include <stdlib.h>
#include "../ports.h"
#include "../io.h"
#include "../boards.h"

#define DIGITAL_DATA_SIZE 1

// Helper routine to get the number of ins and outs indicated by the subtype
static inline void __attribute__ ((always_inline))
break_subtype (uint8_t subtype, unsigned int *n_inp, unsigned int *n_outp)
{
    unsigned int lut[] = {0,1,2,4};
    *n_inp  =  lut[(subtype >> 2) & 0x03];
    *n_outp =  lut[subtype & 0x03];
}

static void digital_read (struct var *var)
{
    module_select(var->board->address);
    var->svar.data[0] = parallel_read(var->address);
}

static void digital_write (struct var *var)
{
    module_select(var->board->address);
    parallel_write(var->address, var->svar.data[0]);
}

void digital_init (struct board *b)
{
    unsigned int n_inp, n_outp, n_ios;

    break_subtype(b->subtype, &n_inp, &n_outp);
    n_ios = n_inp + n_outp;

    unsigned int i;
    for(i = 0; i < n_ios; ++i)
    {
        bool is_input = i < n_inp;
        struct var *v = boards_get_var_slot(DIGITAL_DATA_SIZE);
        v->address            = i;
        v->board              = b;
        v->read_synch         = true;
        v->write_synch        = true;
        v->svar.value_ok      = NULL;
        v->read               = is_input ? digital_read : NULL;
        v->write              = is_input ? NULL : digital_write;
        v->type               = is_input ? VAR_DIGITAL_INPUT:VAR_DIGITAL_OUTPUT;
        v->svar.info.writable = is_input ? false : true;

        if(!is_input)
            digital_write(v);
    }
}
