# -*- Mode: python; py-indent-offset: 4; indent-tabs-mode: nil; coding: utf-8; -*-

from .common import *
from .packet import Packet
from .cwnd_control import CwndControl

from enum import Enum
import time
import sys

class State(Enum):
    INVALID = 0
    SYN = 1
    OPEN = 3
    FIN = 10
    FIN_WAIT = 11
    CLOSED = 20
    ERROR = 21

class Ostream:
    def __init__(self, base = 12345, isOpening = True):
        self.base = base
        self.seqNum = base
        self.lastAckTime = time.time() # last time ACK was sent / activity timer
        self.cc = CwndControl()
        self.buf = b""
        self.state = State.INVALID
        self.nDupAcks = 0

    def ack(self, ackNo, connId):
        if self.state == State.INVALID:
            return None

        ###
        ### IMPLEMENT
        ###
        pass

    def makeNextPacket(self, connId, payload, isSyn=False, isFin=False, **kwargs):
        ###
        ### IMPLEMENT
        ###
        pass

    def hasBufferedData(self):
        ###
        ### IMPLEMENT
        ###
        pass

    def makeNextRetxPacket(self, connId):
        ###
        ### IMPLEMENT
        ###
        pass

    def on_timeout(self, connId):
        ###
        ### IMPLEMENT
        ###
        return None

    def canSendData(self):
        ###
        ### IMPLEMENT
        ###
        pass

    def canSendNewData(self):
        ###
        ### IMPLEMENT
        ###
        pass

    def __str__(self):
        return f"state:{self.state} base:{self.base} seqNum:{self.seqNum} nSentData:{len(self.buf)} cc:{self.cc}"
