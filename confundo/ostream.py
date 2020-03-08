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
    LISTEN = 2

class Ostream:
    def __init__(self, base = 42, isOpening = True):
        self.base = base
        self.seqNum = base
        self.lastAckTime = time.time() # last time ACK was sent / activity timer
        self.cc = CwndControl()
        self.buf = b""
        self.state = State.INVALID
        self.nDupAcks = 0
        self.ackNum = 0
        self.congestionLength = 0

    def ack(self, ackNo, connId):

        dataLen = ackNo - self.seqNum
        self.cc.on_ack( dataLen  )
        self.congestionLength -= (dataLen)
        
        if self.state == State.INVALID:
            return None

        self.seqNum = ackNo        
        if self.state == State.FIN:
            self.state = State.FIN_WAIT
            
        #elif self.state == State.LISTEN:
        #    self.state = State.OPEN
            
        if not self.state == State.FIN_WAIT:            
            self.lastActTime = time.time()
        pass

    def makeNextPacket(self, connId, payload, isSyn=False, isFin=False, **kwargs):
        self.congestionLength += payload.__len__()

        if self.seqNum == MAX_SEQNO:
                self.seqNum = 0
        if isSyn:
            self.state = State.SYN
            pkt = Packet(seqNum=self.seqNum, ackNum=self.ackNum , connId=connId, isSyn=isSyn, isFin=isFin, payload=payload)   
            return pkt                
        
        elif self.state == State.SYN:   
            #self.ackNum += 1         
            pkt = Packet(seqNum=self.seqNum, ackNum=self.ackNum, connId=connId, isSyn=isSyn, isFin=isFin, isAck=True, payload=payload)
            #self.state = State.LISTEN      
            self.state = State.OPEN          
            return pkt
        elif self.state == State.FIN_WAIT:
            pkt = Packet(seqNum=self.seqNum, ackNum=self.ackNum, connId=connId, isSyn=isSyn, isAck=True, isFin=isFin, payload=payload)
            self.state = State.CLOSED
            return pkt
        elif isFin:
            pkt = Packet(seqNum=self.seqNum, ackNum=self.ackNum, connId=connId, isSyn=isSyn, isFin=isFin, payload=payload)
            self.state = State.FIN
            return pkt
            
        if not self.state == State.INVALID:            
            #self.ackNum += 1    
            pkt = Packet(seqNum=self.seqNum, ackNum=self.ackNum, connId=connId, isSyn=isSyn,isFin=isFin, payload=payload)
            #self.state = State.LISTEN         
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
        self.cc.on_timeout()
        diff = time.time() - self.lastAckTime
        if diff > 2.0:
            if self.state == State.CLOSED:
                sys.exit(0)
            return True
        return False

    def canSendData(self):
        pass

    def canSendNewData(self):
        if (self.state == State.OPEN or self.state == State.SYN) and (self.cc.cwnd > self.congestionLength) :
            return True        
        else:
            return False
        pass
        

    def __str__(self):
        return f"state:{self.state} base:{self.base} seqNum:{self.seqNum} nSentData:{len(self.buf)} cc:{self.cc}"
