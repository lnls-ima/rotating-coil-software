#ifndef PUC_BASE_H
#define PUC_BASE_H

#define BASE_BOARD_TYPE     BOARD_BASE

#define BASE_VAR_TYPES      VAR_BASE_DETECTED_BOARDS,\
                            VAR_BASE_SYNC_STATE,\
                            VAR_BASE_SYNC_CONFIG

#define BASE_CURVE_TYPES    CURVE_BASE_RAM,\
                            CURVE_BASE_FLASH

#define BASE_FUNC_TYPES     FUNC_BASE_RESET,\
                            FUNC_BASE_SYNC_START,\
                            FUNC_BASE_SYNC_STOP,\
                            FUNC_BASE_SYNC_PAUSE,\
                            FUNC_BASE_SYNC_STEP

#define BASE_INIT           base_init

#endif
