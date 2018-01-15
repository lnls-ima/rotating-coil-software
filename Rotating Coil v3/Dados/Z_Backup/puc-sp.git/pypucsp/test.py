#!/usr/bin/python

from pypucsp import *
import sys
import time
import math

# Constants
EPSILON = 0.5
LB_TEST_VALUES = (-8.25,-4.75,7.25,3.75,0)
TEST_VALUE = 7.25
TIMEOUT_TIMES = 10
TIMEOUT_DURATION = .1

# Usage string
def usage():
    print("Usage: {} port address".format(sys.argv[0]))
    print("   0 < address < 32")
    exit(0)

def dbgPrint(s):
    l = len(s)
    dots = "."*(46-l)
    sys.stdout.write(s+dots)
    sys.stdout.flush()

def fequals(a, b):
    return abs(a - b) < EPSILON

def waitFor(f, timeout=TIMEOUT_TIMES, duration=TIMEOUT_DURATION):
    while timeout and not f():
        timeout -= 1
        time.sleep(duration)

    return not timeout

# Serial port and PUC serial address
port = None
addr = None

# Run external interrupt tests?
testExternal = True

if len(sys.argv) != 3:
    usage()
else:
    try:
        port = str(sys.argv[1])
        addr = int(sys.argv[2])
    except e:
        usage()

# Start testing
print("")
print("Testing PUC at {} with address {}".format(port, addr))
print("")
dbgPrint("Creating PUC object")
try:
    p = SerialPUC(port, 6e6, addr, debug=False)
except:
    print("FAIL!")
    exit(0)
print("OK!")

AD = None if not p.ads else p.ads[0]
DA = None if not p.das else p.das[0]
DIGOUT = None if not p.digouts else p.digouts[0]

"""dbgPrint("Resetting PUC")
try:
    p.reset()
except:
    pass
time.sleep(1)
print("OK!")"""

dbgPrint("Checking boards")
if not p.das:
    print("FAIL!")
    print("! Connect an analog board")
    exit(0)
print("OK!")

dbgPrint("Stopping any running sync")
if p.sync.getState()[0] != "STOPPED":
    p.sync.stop()
    if p.sync.getState()[0] != "STOPPED":
        print("FAIL!")
        print("! Can't stop the procedure. Check the firmware")
        exit(0)
print("OK!")

dbgPrint("Checking if loopback is present")
for v in LB_TEST_VALUES:
    DA.write(v)
    time.sleep(.1)
    if not fequals(AD.read(),v):
        print("FAIL!")
        print("! Please, connect the D/A to the A/D (loopback)")
        exit(0)
print("OK!")

dbgPrint("Checking if there's an external interrupt")
testExt = SyncConfig()
testExt.inEnabled = False
testExt.outEnabled = True
testExt.clkSource = SyncConfig.CLK_EXTERNAL
testExt.nPoints = 1

p.sync.setConfig(testExt)
p.sync.start()
if waitFor(lambda : p.sync.getState()[0] == "STOPPED"):
    testExternal = False
    print("No external interrupt")
    p.sync.stop()
else:
    print("OK!")

#        (Wide Point, nPoints, type,                  div, genFunc)

tests = [(False,      10,      SyncConfig.CLK_EXTERNAL, 1,   lambda x: x),
         (False,      10,      SyncConfig.CLK_INTERNAL, 3,   lambda x: 5.0),
         (False,      100,     SyncConfig.CLK_INTERNAL, 1,   lambda x: x/10.0),
         (True,       1000,    SyncConfig.CLK_INTERNAL, 1,   lambda x: x/100.0),
         (True,       10000,   SyncConfig.CLK_INTERNAL, 1,   lambda x: x/1000.0),
         (False,      65536,   SyncConfig.CLK_INTERNAL, 1,   lambda x: x/6553.6),
         (True,       32768,   SyncConfig.CLK_INTERNAL, 1,   lambda x: x/3276.8)]

for i,test in enumerate(tests):
    dbgPrint("Running test {}".format(i))

    if not testExternal and test[2] == SyncConfig.CLK_EXTERNAL:
        print("SKIPPED")
        continue

    widePoint, nPoints, clkSource, clkDivisor, f = test
    c = SyncConfig(inEnabled = True, outEnabled = True)
    c.widePoint = widePoint
    c.nPoints = nPoints
    c.clkSource = clkSource
    c.clkDivisor = clkDivisor

    outData = [f(float(x)) for x in range(nPoints)]

    p.sync.stop()
    p.sync.setConfig(c)
    p.sync.outCurve.write(outData, widePoint)
    p.sync.start()

    if clkSource == SyncConfig.CLK_COMM:
        for i in range(nPoints):
            p.sync.step()

    failed = False
    reason = ""

    if waitFor(lambda: p.sync.getState()[0] == "STOPPED", 10, 2):
        failed = True
        fmt = "Wide Point = {}, #points = {}, src = {}, div = {}"
        reason = fmt.format(widePoint, nPoints, clkSource, clkDivisor)
    else:
        inData = p.sync.inCurve.read(nPoints, widePoint)

        if len(inData) != len(outData):
            failed = True
            reason = "In and out curves differ in length"
        else:
            differ = 0
            for inPt, outPt in zip(inData[1:], outData[:-1]):
                if not fequals(inPt, outPt):
                    differ = differ + 1

            # Fail if more than 1% of the points failed
            if float(differ)/len(inData) > 0.01:
                failed = True
                reasonFmt = "In and out points differ in value [{} out of {}]"
                reason = reasonFmt.format(differ, len(inData))

    if failed:
        print("FAIL!")
        print("! {}".format(reason))
    else:
        print("OK!")

print("Done.")

