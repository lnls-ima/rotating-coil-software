#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, math
import hashlib

sys.path.append('../pybsmp/')
import bsmp

def fromRawArray(rawArray):
    raw = 0

    for i in rawArray:
        raw = raw << 8
        raw = raw + i

    return raw

def toRawArray(raw, nBytes):
    rawArray = []
    raw = int(raw)
    for i in range(nBytes):
        rawArray = [raw & 0xFF] + rawArray
        raw = raw >> 8

    return rawArray

def fromRaw(rawArray, bits):
    rawMax = float((1 << bits) - 1)
    raw = fromRawArray(rawArray)

    if raw >= rawMax:
        raw = rawMax
    elif raw < 0:
        raw = 0

    return (20.0*raw)/rawMax - 10.0

def toRaw(value, bits):
    if value < -10.0:
        value = -10.0
    elif value > 10.0:
        value = 10.0

    rawMax = float((1 << bits) - 1)
    raw = (value + 10.0)*rawMax/20.0

    return toRawArray(raw, int(math.ceil(bits/8.0)))

class AD:
    def __init__(self,var):
        self.var = var

    @property
    def id(self):
        return self.var.id

    def read(self):
        return fromRaw(self.var.read(),18)

    def __repr__(self):
        return "(PUC A/D id={})".format(self.id)

class DA:
    def __init__(self,var):
        self.var = var

    @property
    def id(self):
        return self.var.id

    def read(self):
        return fromRaw(self.var.read(),18)

    def write(self, value):
        self.var.write(toRaw(value, 18))

    def __repr__(self):
        return "(PUC D/A id={})".format(self.id)

class DigitalInput:
    def __init__(self,var):
        self.var = var

    @property
    def id(self):
        return self.var.id

    def read(self):
        return self.var.read()[0]

    def __repr__(self):
        return "(PUC DigitalInput id={})".format(self.id)

class DigitalOutput:
    def __init__(self,var):
        self.var = var

    @property
    def id(self):
        return self.var.id

    def read(self):
        return self.var.read()[0]

    def write(self, value):
        self.var.write([value])

    def setBits(self, mask):
        self.var.bitwiseSET([mask])

    def clearBits(self, mask):
        self.var.bitwiseCLEAR([mask])

    def toggleBits(self, mask):
        self.var.bitwiseTOGGLE([mask])

    def __repr__(self):
        return "(PUC DigitalOutput id={})".format(self.id)

class SyncConfig(object):
    CLK_INTERNAL = 0
    CLK_EXTERNAL = 1
    CLK_COMM     = 2
    CLK_SOURCES  = [CLK_INTERNAL, CLK_EXTERNAL, CLK_COMM]
    MIN_POINTS   = 1
    MAX_POINTS   = 65536
    MAX_WPOINTS  = 32768
    MAX_CLK_BIT  = 7
    MIN_CLK_DIV  = 1
    MAX_CLK_DIV  = 65535

    def __init__(self, inEnable=False, outEnable=False, widePoint=False,
                 clkSource=0, nPoints=1, clkDivisor=1, clkOutEnable=False,
                 clkOutBit=0, clkPulseEnable=False, clkPulseBit=0):
        self._inEnable    = inEnable
        self._outEnable   = outEnable
        self._widePoint   = widePoint
        self._clkSource   = clkSource
        self._nPoints     = nPoints
        self._clkDiv      = clkDivisor
        self._clkOutEn    = clkOutEnable
        self._clkOutBit   = clkOutBit
        self._clkPulseEn  = clkPulseEnable
        self._clkPulseBit = clkPulseBit

    def fromArray(self, data):
        self._outEnable   = bool(data[0] & 0x80)
        self._inEnable    = bool(data[0] & 0x40)
        self._widePoint   = bool(data[0] & 0x20)
        self._clkSource   = int((data[0] & 0x18) >> 3) # Bits 3 and 4

        self._nPoints = int((data[1] << 8) | data[2])
        if not self._nPoints:
            self._nPoints = self.MAX_POINTS

        self._clkDiv = int((data[3] << 8) | data[4])

        self._clkOutEn    = bool(data[5] & 0x80)
        self._clkOutBit   = int((data[5] & 0x70) >> 4) # Bits 4, 5 and 6
        self._clkPulseEn  = bool(data[5] & 0x08)
        self._clkPulseBit = int((data[5] & 0x07)) # Bits 0, 1 and 2

    def toArray(self):
        generalCfg = 0
        generalCfg |= int(self._outEnable) << 7
        generalCfg |= int(self._inEnable) << 6
        generalCfg |= int(self._widePoint) << 5
        generalCfg |= int(self._clkSource) << 3
        digitalCfg = 0
        digitalCfg |= int(self._clkOutEn) << 7
        digitalCfg |= int(self._clkOutBit) << 4
        digitalCfg |= int(self._clkPulseEn) << 3
        digitalCfg |= int(self._clkPulseBit)

        nPoints = [(self._nPoints >> 8) & 0xFF, self._nPoints & 0xFF]
        clkDiv  = [(self._clkDiv >> 8) & 0xFF, self._clkDiv & 0xFF]
        return [generalCfg]+nPoints+clkDiv+[digitalCfg]

    @property
    def inEnable(self):
        return self._inEnable

    @inEnable.setter
    def inEnable(self, value):
        self._inEnable = bool(value)

    @property
    def outEnable(self):
        return self._outEnable

    @outEnable.setter
    def outEnable(self, value):
        self._outEnable = bool(value)

    @property
    def widePoint(self):
        return self._widePoint

    @widePoint.setter
    def widePoint(self, value):
        self._widePoint = bool(value)

    @property
    def clkSource(self):
        return self._clkSource

    @clkSource.setter
    def clkSource(self, value):
        if value not in self.CLK_SOURCES:
            raise ValueError
        self._clkSource = value

    @property
    def nPoints(self):
        return self._nPoints

    @nPoints.setter
    def nPoints(self, value):
        if value > self.MAX_POINTS or value < self.MIN_POINTS:
            raise ValueError
        self._nPoints = int(value)

    @property
    def clkDivisor(self):
        return self._clkDiv

    @clkDivisor.setter
    def clkDivisor(self, value):
        if value < self.MIN_CLK_DIV or value > self.MAX_CLK_DIV:
            raise ValueError
        self._clkDiv = int(value)

    @property
    def clkOutEnable(self):
        return self._clkOutEn

    @clkOutEnable.setter
    def clkOutEnable(self, value):
        self._clkOutEn = bool(value)

    @property
    def clkOutBit(self):
        return self._clkOutBit

    @clkOutBit.setter
    def clkOutBit(self, value):
        if value < 0 or value > self.MAX_CLK_BIT:
            raise ValueError
        self._clkOutBit = value

    @property
    def clkPulseEnable(self):
        return self._clkPulseEn

    @clkPulseEnable.setter
    def clkPulseEnable(self, value):
        self._clkPulseEn = bool(value)

    @property
    def clkPulseBit(self):
        return self._clkPulseBit

    @clkPulseBit.setter
    def clkPulseBit(self, value):
        if value < 0 or value > self.MAX_CLK_BIT:
            raise ValueError
        self._clkPulseBit = int(value)

class Sync:
    FUNC_ERROR   = ["OK","Already Running", "Already Paused", "Already Stopped",
                    "Configuration Invalid", "Not Running"]

    def __init__(self,syncVars, syncCurves, syncFuncs, debug):
        self.debug     = debug

        self.state     = syncVars[0]
        self.config    = syncVars[1]

        self.inCurve   = PUCCurve(syncCurves[0])
        self.outCurve  = PUCCurve(syncCurves[1])

        self.startFunc = syncFuncs[0]
        self.stopFunc  = syncFuncs[1]
        self.pauseFunc = syncFuncs[2]
        self.stepFunc  = syncFuncs[3]

    def parseConfig(self, data):
        c = SyncConfig()
        c.fromArray(data)
        return c

    def getConfig(self):
        return self.parseConfig(self.config.read())

    def setConfig(self, cfg):
        self.config.write(cfg.toArray())

    def parseState(self, data):
        states = ("STOPPED", "RUNNING", "PAUSED")
        stateString = states[(data[0] & 0xC0) >> 6]
        index = (data[1] << 16) | (data[2] << 8) | data[3]
        return (stateString, index)

    def getState(self):
        data = self.state.read()
        return self.parseState(data)

    def executeSyncFunc(self, func, debugMsg=""):
        success, data = func.execute()

        if self.debug and not success:
            fmtStr = "{} failure: {}\n"
            errStr = fmtStr.format(debugMsg, self.FUNC_ERROR[data[0]])
            sys.stdout.write(errStr)
        return success

    def start(self):
        return self.executeSyncFunc(self.startFunc, "Sync start")

    def stop(self):
        return self.executeSyncFunc(self.stopFunc, "Sync stop")

    def pause(self):
        return self.executeSyncFunc(self.pauseFunc, "Sync pause")

    def step(self):
        return self.executeSyncFunc(self.stepFunc, "Sync step")

class PUCCurve:
    MAX_POINTS = 65536
    MAX_WIDE_POINTS = MAX_POINTS/2

    def __init__(self, curve):
        self.curve = curve

    @property
    def id(self):
        return self.curve.id

    @property
    def writable(self):
        return self.curve.writable

    @property
    def nBlocks(self):
        return self.curve.nBlocks

    @property
    def blockSize(self):
        return self.curve.blockSize

    @property
    def nBytes(self):
        return self.curve.size

    def nPoints(self, widePoint=False):
        if widePoint:
            return self.nBytes//4 # 4 bytes per point
        else:
            return self.nBytes//2 # 2 bytes per point

    @property
    def cSum(self):
        return self.curve.cSum

    def read(self, nPoints, widePoint=False):

        if not widePoint:
            if nPoints > self.MAX_POINTS:
                raise bsmp.ArgumentError("data")
        else:
            if nPoints > self.MAX_WIDE_POINTS:
                raise bsmp.ArgumentError("data")

        ptSize = 4 if widePoint else 2
        ptBits = 18 if widePoint else 16
        rawData = self.curve.read(nPoints*ptSize)
        data = []
        for i in range(0,len(rawData),ptSize):
            data.append(fromRaw(rawData[i:i+ptSize], ptBits))
        return data

    def write(self, data, widePoint=False, force=False):
        l = len(data)

        if not widePoint:
            if l > self.MAX_POINTS:
                raise bsmp.ArgumentError("data")
        else:
            if l > self.MAX_WIDE_POINTS:
                raise bsmp.ArgumentError("data")

        ptSize = 4 if widePoint else 2
        ptBits = 18 if widePoint else 16
        prepend = [0] if widePoint else []
        rawData = []
        for p in data:
            rawData.extend(prepend+toRaw(p,ptBits))
        self.curve.write(rawData, force)

    def recalcCSum(self):
        return self.curve.recalcCSum()

class PUC:
    DYN_VARS = 3
    def __init__(self, bsmpClient, retries=3, debug=False):
        # Copy arguments
        self.bsmp    = bsmpClient
        self.retries = retries
        self.debug   = debug

        # Read lists of entities
        vars   = self.bsmp.queryVarsList()
        groups = self.bsmp.queryGroupsList()
        curves = self.bsmp.queryCurvesList()
        funcs  = self.bsmp.queryFuncsList()

        # Unwrap lists
        detBoards  = vars[0]
        syncVars   = vars[1:self.DYN_VARS]
        syncCurves = curves
        pucReset   = funcs[0]
        syncFuncs  = funcs[1:]

        # Create detected boards vector
        boardMap = {0:"Analog",1:"Analog Multiplexed",2:"Digital",255:None}
        self.detectedBoards = [boardMap[x] for x in detBoards.read()]

        # Create wrapper objects
        self.pucReset = pucReset

        self.sync = Sync(syncVars, syncCurves, syncFuncs, debug)

        self.ads     = []
        self.das     = []
        self.digins  = []
        self.digouts = []

        for v in vars[self.DYN_VARS:]:
            if v.size == 3:
                if not v.writable:
                    self.ads.append(AD(v))
                else:
                    self.das.append(DA(v))
            else:
                if not v.writable:
                    self.digins.append(DigitalInput(v))
                else:
                    self.digouts.append(DigitalOutput(v))

    def readAll(self):
        values = self.bsmp.queryGroupsList()[0].read()
        parsed = dict()
        parsed["SyncState"] = self.sync.parseState(values[self.sync.state])
        parsed["SyncConfig"] = self.sync.parseConfig(values[self.sync.config])

        for a in self.ads+self.das:
            parsed[a] = fromRaw(values[a.var],18)

        for d in self.digins+self.digouts:
            parsed[d] = values[d.var][0]

        return parsed

    def reset(self):
        self.pucReset.execute()

    def disconnect(self):
        self.bsmp.disconnect()

class TCPPUC(PUC):
    def __init__(self, ip, port, retries=3, debug=False):
        cli = bsmp.TCPClient(ip, port, retries, debug)
        PUC.__init__(self, cli, retries, debug)

class SerialPUC(PUC):
    def __init__(self, port, address, baud=6000000, retries=3, debug=False):
        cli = bsmp.SerialClient(port, baud, address, retries, debug)
        PUC.__init__(self, cli, retries, debug)

