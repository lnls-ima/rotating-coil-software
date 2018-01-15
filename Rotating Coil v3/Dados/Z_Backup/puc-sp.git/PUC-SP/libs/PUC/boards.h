#ifndef PUC_BOARDS_H
#define PUC_BOARDS_H

#include <stdint.h>
#include <stdbool.h>
#include <server.h>

#include <bsmp.h>
#include "boards/base.h"
#include "boards/analog.h"
#include "boards/digital.h"

enum board_type
{
    BASE_BOARD_TYPE,
    ANALOG_BOARD_TYPE,
    DIGITAL_BOARD_TYPE,
    BOARD_TYPE_MAX,
};

enum var_type
{
    BASE_VAR_TYPES,
    ANALOG_VAR_TYPES,
    DIGITAL_VAR_TYPES,
    VAR_TYPE_MAX,
};

enum curve_type
{
    BASE_CURVE_TYPES,
    CURVE_TYPE_MAX,
};

enum func_type
{
    BASE_FUNC_TYPES,
    FUNC_TYPE_MAX,
};

// Forward declarations
struct board;
struct var;

extern void BASE_INIT    (struct board *b);
extern void ANALOG_INIT  (struct board *b);
extern void DIGITAL_INIT (struct board *b);

// Function typedefs

typedef void (*init_func_t) (struct board *);
typedef void (*rw_func_t)   (struct var *);

struct board_info
{
    uint8_t real_type;
    init_func_t init;
};

struct board
{
    enum board_type type;
    uint8_t real_type;
    uint8_t subtype;
    uint8_t address;
};

struct var
{
    enum var_type type;
    struct board *board;
    uint8_t address;
    rw_func_t read;
    rw_func_t write;
    bool read_synch;
    bool write_synch;
    struct bsmp_var svar;
};

struct curve
{
    enum curve_type type;
    struct board *board;
    uint16_t first_block;
    struct bsmp_curve scurve;
};

struct func
{
    enum func_type type;
    struct board *board;
    struct bsmp_func sfunc;
};

struct var   *boards_get_var_slot   (uint8_t data_size);
struct curve *boards_get_curve_slot (void);
struct func  *boards_get_func_slot  (void);

struct var   *boards_get_first_var  (enum var_type type);

void boards_init (bsmp_server_t *server);
void boards_hook (enum bsmp_operation op, struct bsmp_var **list);
void boards_get_detected_types (uint8_t *data);

#endif
