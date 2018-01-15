/*
 * This file contains routines that handle the detection and initialization
 * of boards attached to the base and the base itself. Also contains the hook
 * that is passed to the BSMP library instance.
 *
 * About board types:
 *
 * The type of a board is read from the address PORTS_DESC_ADDR (7) from the
 * parallel bus. The high nibble contains the type, the low nibble the subtype.
 *
 * If the whole byte reads NO_BOARD (255), then there is no board present.
 * If the whole byte contains the value READ_NEXT_ADDR (254), then the type and
 * subtype of the board must be read from the address PORTS_DESC_EXTENDED (5).
 * The type then will be the value found in the high nibble, plus 16.
 *
 * Therefore boards have 5-bits for their type (0~31) and 4 bits for their
 * subtype (0~15).
 *
 * However, in this module (boards), there is a virtual board named 'base', with
 * a virtual type 254 (well above the maximum real type, 31).
 */

#include "boards.h"
#include "ports.h"
#include "sync.h"

#include <stdlib.h>
#include <string.h>

#define NO_BOARD        255
#define MAX_REAL_BOARDS 4
#define MAX_BOARDS      1+MAX_REAL_BOARDS
#define MAX_VARS        128
#define MAX_CURVES      128
#define MAX_FUNCS       128

#define MAX_VARS_MEMORY 256

static struct
{
    struct board list[MAX_BOARDS];
    unsigned int count;
}boards = { .count = 0 };

static struct
{
    struct
    {
        uint8_t  data[MAX_VARS_MEMORY];
        uint32_t allocated;
    }memory;

    struct var   list[MAX_VARS];
    unsigned int count;
}vars = { .memory.allocated = 0, .count = 0 };

static struct
{
    struct curve list[MAX_CURVES];
    unsigned int count;
}curves = { .count = 0 };

static struct
{
    struct func  list[MAX_FUNCS];
    unsigned int count;
}funcs = { .count = 0 };

// Infos

struct board_info board_info[BOARD_TYPE_MAX] = {
    [BOARD_BASE]    = {254, BASE_INIT},     // Real type, init function
    [BOARD_ANALOG]  = {0,   ANALOG_INIT},
    [BOARD_DIGITAL] = {2,   DIGITAL_INIT},
};

static inline struct board *get_board_slot (void)
{
    return &boards.list[boards.count++];
}

// Returns true if missing
static inline bool read_type_subtype (uint8_t *type, uint8_t *subtype)
{
    bool extended_type = false;
    uint8_t whole_type = parallel_read(PORTS_DESC_ADDR);

    if(whole_type == PORTS_DESC_NO_BOARD)
        return true;    // missing

    if(whole_type == PORTS_DESC_READ_NEXT)
    {
        whole_type = parallel_read(PORTS_DESC_EXTENDED);
        extended_type = true;
    }

    *type = (whole_type >> 4) + 16*extended_type;
    *subtype = whole_type & 0x0F;
    return false; // not missing
}

// Initialize the boards module
void boards_init(bsmp_server_t *server)
{
    unsigned int i;

    // Initialize the base board
    base_init(get_board_slot());

    // Search for description var
    struct var *desc_var = boards_get_first_var(VAR_BASE_DETECTED_BOARDS);

    // Search for possible attached boards
    for(i = 0; i < MAX_REAL_BOARDS; ++i)
    {
        uint8_t real_type, subtype;

        // Set the type of the board i to the default NO_BOARD
        if(desc_var)
            desc_var->svar.data[i] = PORTS_DESC_NO_BOARD;

        module_select(i);
        if(read_type_subtype(&real_type, &subtype))
            continue;

        // Search virtual type from real type
        enum board_type type = 0;
        for(type = 0; type < BOARD_TYPE_MAX; type++)
            if(board_info[type].real_type == real_type)
                break;

        // Test if it is an unrecognized board type
        if(type == BOARD_TYPE_MAX)
            continue;

        // Test if it has an init function
        if(!board_info[type].init)
            continue;

        // Fill the structure with information about the board found
        struct board *b = get_board_slot();
        b->address      = i;
        b->type         = type;
        b->real_type    = real_type;
        b->subtype      = subtype;

        board_info[type].init(b);

        if(desc_var)
            desc_var->svar.data[i] = real_type;
    }

    for(i = 0; i < vars.count; ++i)
        bsmp_register_variable(server, &vars.list[i].svar);

    for(i = 0; i < curves.count; ++i)
        bsmp_register_curve(server, &curves.list[i].scurve);

    for(i = 0; i < funcs.count; ++i)
        bsmp_register_function(server, &funcs.list[i].sfunc);
}

static void read_vars (struct bsmp_var **list)
{
    struct bsmp_var *svar;
    bool pulsed = false;

    while((svar = *list++))
    {
        struct var *var = (struct var *) svar->user;

        if(var->read)
        {
            // Don't access the boards SPI if sync is running
            if(sync_get_state() == SYNC_RUNNING &&
                    var->type > VAR_BASE_SYNC_CONFIG)
                continue;

            if(var->read_synch && !pulsed)
            {
                pulse_syn_input();
                pulsed = true;
            }
            var->read(var);
        }
    }
}

static void write_vars (struct bsmp_var **list)
{
    // If sync is running, don't mess with the system
    if(sync_get_state() == SYNC_RUNNING)
        return;

    struct bsmp_var *svar;
    bool has_to_pulse = false;

    while((svar = *list++))
    {
        struct var *var = (struct var *) svar->user;

        if(var->write)
        {
            var->write(var);
            if(var->write_synch)
                has_to_pulse = true;
        }
    }

    if(has_to_pulse)
        pulse_syn_output();
}

// This is called by the BSMP library. Read the BSMP documentation about it.
void boards_hook (enum bsmp_operation op, struct bsmp_var **list)
{
    op == BSMP_OP_READ ? read_vars(list) : write_vars(list);
}

// Get first free var slot and allocate data_size bytes to that variable
struct var *boards_get_var_slot (uint8_t data_size)
{
    if(vars.count >= MAX_VARS)
        return NULL;

    if(vars.memory.allocated + data_size > MAX_VARS_MEMORY)
        return NULL;

    struct var *v = &vars.list[vars.count++];
    v->svar.data = &vars.memory.data[vars.memory.allocated];
    v->svar.user = (void*) v;
    v->svar.info.size = data_size;
    vars.memory.allocated += data_size;
    return v;
}

struct curve *boards_get_curve_slot (void)
{
    if(curves.count >= MAX_CURVES)
        return NULL;

    struct curve *c = &curves.list[curves.count++];
    c->scurve.user = (void*) c;
    return c;
}

struct func *boards_get_func_slot  (void)
{
    return funcs.count >= MAX_FUNCS ? NULL : &funcs.list[funcs.count++];
}

// Get the first variable of the given type
struct var *boards_get_first_var (enum var_type type)
{
    unsigned int i;
    for(i = 0; i < vars.count; ++i)
        if(vars.list[i].type == type)
            break;

    return i == vars.count ? NULL : &vars.list[i];
}
