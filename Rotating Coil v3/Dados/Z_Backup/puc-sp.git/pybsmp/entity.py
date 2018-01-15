# -*- coding: utf-8 -*-

from exception  import *
from command    import *
import hashlib
import math

def parseMD5(rawMD5):
    return "".join(map(lambda x: "{:02x}".format(x), rawMD5))

class Version:
    def __init__(self, version, subversion, revision):
        self.version    = version
        self.subversion = subversion
        self.revision   = revision

    def __repr__(self):
        return "{:d}.{:02d}.{:03d}".format(self.version,self.subversion,\
                                           self.revision)

class Variable:
    def __init__(self, client, id, writable, size):
        self.client   = client
        self.cmd      = client.sendCommand
        self.id       = int(id)
        self.writable = bool(writable)
        self.size     = int(size)

    def __repr__(self):
        return "Var(id={},wr={},sz={})".format(self.id,self.writable,self.size)

    def read(self):
        _,val = self.cmd(CMD_READ_VAR, [self.id], [CMD_VAR_READING],\
                         lambda x: x == self.size)
        return val

    def write(self, value):
        if not self.writable:
            raise ReadOnlyError(self)
        if len(value) != self.size:
            raise ArgumentError("value")

        self.cmd(CMD_WRITE_VAR, [self.id]+value, [CMD_OK,CMD_ERR_INVALID_VALUE],\
                 lambda x: x == 0)

    def writeAndRead(self, value, readVar):
        if not self.writable:
            raise ReadOnlyError(self)

        if len(value) != self.size:
            raise ArgumentError("value")

        _,retVal = self.cmd(CMD_WRITE_READ_VARS,[self.id, readVar.id]+value,\
                            [CMD_VAR_READING], lambda x: x == readVar.size)
        return retVal

    def bitwiseOp(self, op, mask):
        if op not in map(ord,"AOXSCT"):
            raise ArgumentError("op")
        if not self.writable:
            raise ReadOnlyError(self)
        if len(mask) != self.size:
            raise ArgumentError("mask")

        self.cmd(CMD_BIN_OP_VAR, [self.id,op]+mask, [CMD_OK], lambda x: x == 0)

    def bitwiseAND(self, mask):
        self.bitwiseOp(ord('A'),mask)

    def bitwiseOR(self, mask):
        self.bitwiseOp(ord('O'),mask)

    def bitwiseXOR(self, mask):
        self.bitwiseOp(ord('X'),mask)

    def bitwiseSET(self, mask):
        self.bitwiseOp(ord('S'),mask)

    def bitwiseCLEAR(self, mask):
        self.bitwiseOp(ord('C'),mask)

    def bitwiseTOGGLE(self, mask):
        self.bitwiseOp(ord('T'),mask)

class Group:
    def __init__(self, client, id, writable, varIds):
        self.client    = client
        self.cmd       = client.sendCommand
        self.id        = int(id)
        self.writable  = bool(writable)

        self.vars      = []
        self.size      = 0

        for i in varIds:
            self.vars.append(client.queryVarsList()[i])
            self.size += self.vars[-1].size

    def __repr__(self):
        return "Grp(id={},wr={},nvars={})".format(self.id, self.writable,\
                                                  len(self.vars))

    def __getitem__(self,i):
        return self.vars[i]

    def read(self):
        _,values = self.cmd(CMD_READ_GROUP, [self.id], [CMD_GROUP_READING],\
                            lambda x: x == self.size)
        groupedValues = []
        for v in self.vars:
            groupedValues.append(values[:v.size])
            values = values[v.size:]
        return dict(zip(self.vars, groupedValues))

    def write(self, groupedValues):
        if not self.writable:
            raise ReadOnlyError(self)

        if len(groupedValues) != len(self.vars):
            raise ArgumentError("groupedValues")

        values = []
        for val in groupedValues:
            values.extend(val)

        if len(values) != self.size:
            raise ArgumentError("groupedValues")

        self.cmd(CMD_WRITE_GROUP, [self.id]+values, [CMD_OK], lambda x: x == 0)

    def bitwiseOp(self, op, groupedMasks):
        if op not in map(ord,"AOXSCT"):
            raise ArgumentError("op")

        if not self.writable:
            raise ReadOnlyError(self)

        if len(groupedMasks) != len(self.vars):
            raise ArgumentError("groupedMasks")

        masks = []
        for mask in groupedMasks:
            masks.extend(mask)

        if len(masks) != self.size:
            raise ArgumentError("groupedMasks")

        self.cmd(CMD_BIN_OP_GROUP, [self.id,op]+masks, [CMD_OK],\
                 lambda x: x == 0)

    def bitwiseAND(self, groupedMasks):
        self.bitwiseOp(ord('A'),groupedMasks)

    def bitwiseOR(self,groupedMasks):
        self.bitwiseOp(ord('O'),groupedMasks)

    def bitwiseXOR(self,groupedMasks):
        self.bitwiseOp(ord('X'),groupedMasks)

    def bitwiseSET(self,groupedMasks):
        self.bitwiseOp(ord('S'),groupedMasks)

    def bitwiseCLEAR(self, mask):
        self.bitwiseOp(ord('C'),groupedMasks)

    def bitwiseTOGGLE(self, mask):
        self.bitwiseOp(ord('T'),mask)

class Curve:
    def __init__(self, client, id, writable, nBlocks, blockSize, cSum):
        self.client    = client
        self.cmd       = client.sendCommand
        self.id        = int(id)
        self.writable  = bool(writable)
        self.nBlocks   = int(nBlocks)
        self.blockSize = int(blockSize)
        self.size      = self.nBlocks*self.blockSize
        self.cSum      = parseMD5(cSum)

    def __repr__(self):
        fmt = "Cur(id={},wr={},nblk={},blksz={})"
        return fmt.format(self.id,self.writable,self.nBlocks,self.blockSize)

    def readBlock(self, blockNumber):
        if blockNumber < 0 or blockNumber >= self.nBlocks:
            raise ArgumentError("blockNumber")

        _,data =  self.cmd(CMD_TRANSMIT_CURVE_BLOCK,\
                           [self.id, blockNumber>>8, blockNumber&0xFF],\
                           [CMD_CURVE_BLOCK],\
                           lambda x: x >= 3)
        return data[3:]

    def read(self, nBytes=None):
        if nBytes == None:
            nBytes = self.size

        nBlocks = int(math.ceil(float(nBytes)/self.blockSize))
        data = []
        for i in range(nBlocks):
            blk = self.readBlock(i)
            data.extend(blk)
            if len(blk) < self.blockSize:
                return data

        return data[:nBytes]

    def writeBlock(self, blockNumber, blockData):
        if not self.writable:
            raise ReadOnlyError(self)

        if blockNumber < 0 or blockNumber >= self.nBlocks:
            raise ArgumentError("blockNumber")

        if len(blockData) > self.blockSize:
            raise ArgumentError("blockData")

        self.cmd(CMD_CURVE_BLOCK,\
                 [self.id, blockNumber>>8,blockNumber&0xFF]+blockData,\
                 [CMD_OK], lambda x: x == 0)

    def write(self, data, force = False):
        if not self.writable:
            raise ReadOnlyError(self)

        if len(data) > self.size or len(data) == 0:
            raise ArgumentError("data")

        if not force:
            digest = hashlib.md5(bytearray(data)).hexdigest()
            if digest == self.cSum:
                return

        for i in range(self.nBlocks):
            blockSize = min(len(data),self.blockSize)
            blockData = data[:blockSize]
            self.writeBlock(i, blockData)

            data = data[blockSize:]
            if not data:
                break

        self.recalcCSum()

    def recalcCSum(self):
        _,rawMD5 = self.cmd(CMD_RECALC_CHECKSUM,[self.id], [CMD_CURVE_CSUM],\
                            lambda x: x == 16)

        self.cSum = parseMD5(rawMD5)
        return self.cSum


class Function:
    def __init__(self, client, id, input, output):
        self.client    = client
        self.cmd       = client.sendCommand
        self.bcast     = client.sendBroadcast
        self.id        = int(id)
        self.input     = int(input)
        self.output    = int(output)

    def __repr__(self):
        return "Fun(id={},in={},out={})".format(self.id,self.input,self.output)

    def execute(self, inputData = []):
        if len(inputData) != self.input:
            raise ArgumentError("inputData")

        code,data = self.cmd(CMD_EXECUTE_FUNCTION,[self.id]+inputData,\
                             [CMD_FUNCTION_RETURN,CMD_FUNCTION_ERROR])

        return code == CMD_FUNCTION_RETURN, data

    def broadcast(self, inputData = []):
        if len(inputData) != self.input:
            raise ArgumentError("inputData")

        self.bcast(CMD_EXECUTE_FUNCTION,[self.id]+inputData)

