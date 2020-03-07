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
    def __init__(self, base=12345, isOpening=True):
        self.base = base
        self.seqNum = base
        self.lastAckTime = time.time()  # last time ACK was sent / activity timer
        self.cc = CwndControl()
        self.buf = b""
        self.state = State.INVALID
        self.nDupAcks = 0
        self.ackNum = 0

    def ack(self, ackNo, connId):
        if self.state == State.INVALID:
            print("state is invalid")
            return None

        self.lastAckTime = time.time()
        pass


    def makeNextPacket(self, connId, payload, isSyn=False, isFin=False, isAck = False, **kwargs):
        if self.seqNum == MAX_SEQNO:
            self.seqNum = 0
        pkt = Packet(seqNum=self.seqNum, ackNum = self.ackNum, connId=connId, isSyn=isSyn, isFin=isFin, payload=payload, isAck = isAck)
        self.seqNum += 1
        self.state = State.OPEN
        return pkt
        
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
        if 10 <= (time.time() - self.lastAckTime):
            return True
        return None

    def canSendData(self):
        if self.state == State.OPEN:
            return True
        else:
            return False

    def canSendNewData(self, cwnd_control, congestionLength):
        self.cwnd_control = cwnd_control
        self.congestionLength = congestionLength
        #Send only if state is open and cwnd is less than the actual congestion length
        if self.state == State.OPEN and (self.cwnd_control.cwnd > self.congestionLength):
            return True
        else:
            return False

    def __str__(self):
        return f"state:{self.state} base:{self.base} seqNum:{self.seqNum} nSentData:{len(self.buf)} cc:{self.cc}"
