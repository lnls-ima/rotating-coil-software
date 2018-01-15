# -*- coding: utf-8 -*-

from exception import *
from entity    import *
from command   import *
import serial
import socket
import sys

HEADER_SIZE = 3

def printMessage(msgType, msg):
    if not msg:
        sys.stderr.write("{:s} Empty message\n".format(msgType))
    elif len(msg) < 3:
        sys.stderr.write("{:s} Short (malformed) message\n".format(msgType))
    else:
        code, length = msg[0], (msg[1]<<8)+msg[2]

        preStr      = "{:s} [{:02X} {:d} bytes]".format(msgType,code,length)
        payloadStr  = ""
        payload     = msg[3:]

        if len(payload) and len(payload) < 20:
            payloadStr = ": "+" ".join(["{:02X}".format(b) for b in payload])

        sys.stderr.write(preStr+payloadStr+"\n")

class Client:
    def __init__(self, sendFunction, recvFunction, retries=3, debug=False):
        self.retries = retries+1
        self.debug   = debug
        self.send    = sendFunction
        self.recv    = recvFunction

        self.version    = None
        self.varsList   = None
        self.groupsList = None
        self.curvesList = None
        self.funcsList  = None

    def disconnect(self):
        pass

    def update(self, force=False):
        self.queryVersion(force)
        self.queryVarsList(force)
        self.queryCurvesList(force)
        self.queryGroupsList(force)
        self.queryFuncsList(force)

    def sendBroadcast(self, cmd, payload):
        length  = len(payload)
        request = [cmd, (length >> 8) & 0xFF, length & 0xFF] + payload
        self.send(request, True)

    def sendCommand(self, cmd, payload, expectedAnswer = None, payloadOk = None):
        # Prepare request
        length  = len(payload)
        request = [cmd, (length >> 8) & 0xFF, length & 0xFF] + payload

        for i in range(self.retries):
            if i and self.debug:
                sys.stderr.write("RETRY: {}/{} ".format(i,self.retries-1))

            # Send request
            if self.debug:
                printMessage("REQ",request)
            self.send(request)

            # Get response
            response = self.recv()
            if self.debug:
                printMessage("RES", response)

            # Check response
            if not response:
                if i+1 < self.retries:
                    continue
                raise NoAnswerError(request)

            pSize = 0
            if len(response) >= HEADER_SIZE:
                pSize = (response[1] << 8) + response[2]

            if len(response) < HEADER_SIZE or len(response) != HEADER_SIZE+pSize:
                if i+1 < self.retries:
                    continue
                raise MalformedAnswerError(request,response)

            if response[0] > 0xE0 and response[0] <= 0xEF:
                raise ServerError(request,response[0])

            if expectedAnswer != None and response[0] not in expectedAnswer:
                raise CommandError(req,response,expectedAnswer)

            if payloadOk and not payloadOk(pSize):
                raise SizeError(request,response)

            # Return response code and payload
            return response[0],response[3:]

    def queryVersion(self, force = False):
        if self.version == None or force:
            _, res = self.sendCommand(CMD_QUERY_VERSION, [], \
                                      [CMD_VERSION], lambda x: x == 3)
            self.version = Version(res[0], res[1], res[2])
        return self.version

    def queryVarsList(self, force = False):
        if self.varsList == None or force:
            _, res = self.sendCommand(CMD_QUERY_VARS_LIST, [],\
                                      [CMD_VARS_LIST])
            self.varsList = [Variable(self,i,v&0x80,v&0x7F) \
                             for i,v in enumerate(res)]
        return self.varsList

    def queryGroupsList(self, force = False):
        if self.groupsList == None or force:
            _, res = self.sendCommand(CMD_QUERY_GROUPS_LIST, [],\
                                      [CMD_GROUPS_LIST])

            gList = []
            for i, value in enumerate(res):
                gId = i
                gWritable = value & 0x80
                _, gVars = self.sendCommand(CMD_QUERY_GROUP, [gId],\
                                            [CMD_GROUP])

                gList.append(Group(self, gId, gWritable, gVars))

            self.groupsList = gList

        return self.groupsList

    def queryCurvesList(self, force = False):
        if self.curvesList == None or force:
            _,res = self.sendCommand(CMD_QUERY_CURVES_LIST,[],\
                                     [CMD_CURVES_LIST])

            cList = []
            for i in range(0, len(res), 5):
                cId        = i//5
                cWritable  = res[i]
                cBlockSize = (res[i+1] << 8)+(res[i+2])
                cBlocks    = (res[i+3] << 8)+(res[i+4])

                if not cBlocks:
                    cBlocks = 65536

                _, cRawCSum = self.sendCommand(CMD_QUERY_CURVE_CSUM,[cId],\
                                               [CMD_CURVE_CSUM])
                cList.append(Curve(self, cId, cWritable, cBlocks, cBlockSize,\
                                   cRawCSum))
            self.curvesList = cList

        return self.curvesList

    def queryFuncsList(self, force = False):
        if self.funcsList == None or force:
            _, res = self.sendCommand(CMD_QUERY_FUNCS_LIST, [], [CMD_FUNCS_LIST])

            self.funcsList = \
                        [Function(self,i,v>>4,v&0x0F) for i,v in enumerate(res)]

        return self.funcsList

    def groupCreate(self, variables):
        self.sendCommand(CMD_CREATE_GROUP, [v.id for v in variables], [CMD_OK],\
                         lambda x: x == 0)

    def groupRemoveAll(self):
        self.sendCommand(CMD_REMOVE_ALL_GROUPS, [], [CMD_OK], lambda x: x == 0)

class TCPClient(Client):
    def __init__(self, ip, port, retries=3, debug=False):
        self.s    = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        Client.__init__(self, self.sendFunc, self.recvFunc, retries, debug)
        self.ip   = ip
        self.port = port

        self.s.connect((ip,port))

    def sendFunc(self, message):
        self.s.send(bytearray(message))

    def recvFunc(self):
        header = bytearray(self.s.recv(3))

        tam = (header[1] << 8) | header[2]

        if not tam:
            return list(header)

        body = bytearray(self.s.recv(tam))

        return list(header + body)

    def disconnect(self):
        self.s.close()

class SerialClient(Client):
    def __init__(self, serPort, serBaud, serAddress, retries=3, debug=False):
        Client.__init__(self, self.sendFunc, self.recvFunc, retries, debug)
        self.s    = serial.Serial(serPort, serBaud, timeout=1)
        self.addr = serAddress

    def sendFunc(self, message):
        message = [self.addr]+message
        cSum    = (0x100 - (sum(message) & 0xFF)) & 0xFF
        message.append(cSum)
        self.s.write(bytearray(message))

    def disconnect(self):
        self.s.close()

    def recvFunc(self):
        header = bytearray(self.s.read(1+HEADER_SIZE)) # ADDR + HEADER

        if not header:
            if self.debug:
                sys.stderr.write("Empty header\n")
            return []

        bodySize = (header[-2] << 8) | header[-1] + 1 # +1 for CSum

        body = bytearray(self.s.read(bodySize))

        if header[0] != 0:  # Ignore packet
            if self.debug:
                sys.stderr.write("Got stray packet\n")
            return []

        cSum = (sum(header)+sum(body)) & 0xFF
        if cSum:
            if self.debug:
                sys.stderr.write("Checksum error\n")
                sys.stderr.write(" Value:{}\n".format(cSum))
                sys.stderr.write(" Body size:{}\n".format(len(body)))
            return []

        return list(header[-3:]+body[:-1])
