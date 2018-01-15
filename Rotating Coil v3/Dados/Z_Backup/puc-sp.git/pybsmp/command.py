# -*- coding: utf-8 -*-

import collections

CMD_QUERY_VERSION = 0x00
CMD_VERSION = 0x01
CMD_QUERY_VARS_LIST = 0x02
CMD_VARS_LIST = 0x03
CMD_QUERY_GROUPS_LIST = 0x04
CMD_GROUPS_LIST = 0x05
CMD_QUERY_GROUP = 0x06
CMD_GROUP = 0x07
CMD_QUERY_CURVES_LIST = 0x08
CMD_CURVES_LIST = 0x09
CMD_QUERY_CURVE_CSUM = 0x0A
CMD_CURVE_CSUM = 0x0B
CMD_QUERY_FUNCS_LIST = 0x0C
CMD_FUNCS_LIST = 0x0D
CMD_READ_VAR = 0x10
CMD_VAR_READING = 0x11
CMD_READ_GROUP = 0x12
CMD_GROUP_READING = 0x13
CMD_WRITE_VAR = 0x20
CMD_WRITE_GROUP = 0x22
CMD_BIN_OP_VAR = 0x24
CMD_BIN_OP_GROUP = 0x26
CMD_WRITE_READ_VARS = 0x28
CMD_CREATE_GROUP = 0x30
CMD_REMOVE_ALL_GROUPS = 0x32
CMD_TRANSMIT_CURVE_BLOCK = 0x40
CMD_CURVE_BLOCK = 0x41
CMD_RECALC_CHECKSUM = 0x42
CMD_EXECUTE_FUNCTION = 0x50
CMD_FUNCTION_RETURN = 0x51
CMD_FUNCTION_ERROR = 0x53
CMD_OK = 0xE0
CMD_ERR_MALFORMED_MSG = 0xE1
CMD_ERR_OP_NOT_SUPPORTED = 0xE2
CMD_ERR_INVALID_ID = 0xE3
CMD_ERR_INVALID_VALUE = 0xE4
CMD_ERR_INVALID_PAYLOAD_SIZE = 0xE5
CMD_ERR_READ_ONLY = 0xE6
CMD_ERR_INSUFFICIENT_MEMORY = 0xE7


Command = collections.namedtuple("Command", ['name', 'code', 'payloadFunc'])

binOps = {"AND":ord('A'), "OR":ord('O'),  "XOR":ord('X'),
          "SET":ord('S'), "CLR":ord('C'), "TOGGLE":ord('T')}

binOpByName   = {x[0]  : x for x in binOps}
binOpByCode   = {x[1]  : x for x in binOps}

def versionInfo(msg):
    return "{:d}.{:02d}.{:03d}".format(msg[0],msg[1],msg[2])

def idSizeWritableList(msg):
    fmt = "(ID={},SZ={},WR={})"
    return ",".join([fmt.format(i,v&0x7F,v>=0x80) for i,v in enumerate(msg)])

def singleId(msg):
    return "ID={}".format(msg[0])

def idList(msg):
    return "IDS="+",".join(["{}".format(i) for i in msg])

def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i+n]

def curvesList(msg):
    fmt = "(ID={},WR={},BLKSZ={},BLKS={})"
    curvesStr = []
    for i,c in enumerate(chunks(msg,5)):
        curvesStr.append(fmt.format(i,c[0], (c[1] << 8) + c[2], (c[3] << 8) + c[4]))
    return ",".join(curvesStr)

def funcsList(msg):
    fmt = "(ID={},IN={},OUT={})"
    return ",".join([fmt.format(i, (v&0xF0)>>4, v&0x0F) for i,v in enumerate(msg)])

def bytesList(msg):
    return "".join( ["{:02x}".format(v) for v in msg] )

def cSumBytes(msg):
    return "CSUM="+bytesList(msg)

def singleValue(msg):
    return "VALUE="+bytesList(msg)

def singleIdValue(msg):
    return singleId(msg[:1])+" "+singleValue(msg[1:])

def twoIdsValue(msg):
    s = singleId([msg[0]])+" "
    s = s + singleId([msg[1]])+" "
    s = s + singleValue(msg[2:])
    return s

def singleOp(code):
    return "OP="+binOpByCode[msg[1]]

def singleIdOpValue(msg):
    return singleId(msg[:1])+" "+singleOp(msg[1])+" "+singleValue(msg[2:])

def idAndList(msg):
    return singleId(msg[:1])+" "+str(msg[1:])

def idOpAndList(msg):
    return singleId(msg[:1])+" "+singleOp(msg[1])+" "+str(msg[2:])

def curveBlock(msg):
    return singleId(msg[:1])+",BLOCK={:d}".format((msg[1]<<8)+msg[2])

def curveBlockData(msg):
    return curveBlock(msg)+" plus 16834 bytes"

def funcError(msg):
    return "ERROR CODE=0x{:02X}".format(msg[0])


def isError(cmd):
    code = 0

    if type(cmd) == int:
        code = cmd
    elif cmd.__class__ == Command:
        code = cmd.code
    else:
        raise TypeError("Expecting 'int' or 'bsmp.Command'")

    return code > 0xE0 and code <= 0xEF


