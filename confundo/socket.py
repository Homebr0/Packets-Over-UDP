# -*- Mode: python; py-indent-offset: 4; indent-tabs-mode: nil; coding: utf-8; -*-

import sys
import time

from .common import *
from .istream import Istream
from .ostream import Ostream, State
from .packet import Packet
import multiprocessing


class Socket:
    '''Incomplete socket abstraction for Confundo protocol'''

    def __init__(self, sock, connId=0):
        self.sock = sock
        self.connId = connId
        self.sock.settimeout(0.5)
        self.istream = None
        self.ostream = None
        self.closing = False
        self.closingActReceived = False

    def format_line(self, command, pkt):
        s = f"{command} {pkt.seqNum} {pkt.ackNum} {pkt.connId} {int(self.ostream.cc.cwnd)} {self.ostream.cc.ssthresh}"
        if pkt.isAck: s = s + " ACK"
        if pkt.isSyn: s = s + " SYN"
        if pkt.isFin: s = s + " FIN"
        if pkt.isDup: s = s + " DUP"
        return s

    def _send(self, packet):
        '''"Private" method to send packet out'''

        self.sock.sendto(packet.encode(), self.remote)
        print(self.format_line("SEND", packet))

    def on_receive(self, buf):
        '''Method that dispatches the received packet'''
        pkt = Packet().decode(buf)
        print(self.format_line("RECV", pkt))

        self.ostream.ack(pkt.ackNum, pkt.connId)

        temp = pkt.ackNum
        self.ostream.ackNum = pkt.seqNum + 1
        self.ostream.seqNum = temp

        if self.closing:
                if pkt.isAck and not pkt.isFin and not pkt.isSyn: #Expect packet with ACK flag
                    self.ostream.state = State.FIN_WAIT
                    self.closingAckReceived = True
                elif pkt.isFin and self.closingAckReceived: #
                    newPkt = self.ostream.makeNextPacket(self.connId, payload = b'', isAck=True)
                    self._send(newPkt)
                elif not pkt.isAck:
                    print("ERROR: ACK Flag Expected")
                else:
                    pass #drop any other non-FIN packet

        if pkt.isSyn and pkt.isAck:
            print("SYN-ACK received")
            self.connId = pkt.connId


    def process_retransmissions(self):

        ###
        ### IMPLEMENT
        ###

        pass

    def on_timeout(self):
        '''Called every 0.5 seconds if nothing received'''

        if self.ostream.on_timeout(self.connId):
            return True

        return False

    def connect(self, remote):
        self.remote = remote
        self.ostream = Ostream(base = 42)
        
        pkt = self.ostream.makeNextPacket(connId=0, payload=b"", isSyn=True)
        self._send(pkt)

    def canSendData(self):
        return self.ostream.canSendNewData()

    def send(self, payload):
        pkt = self.ostream.makeNextPacket(self.connId, payload, isAck=True)
        self._send(pkt)

    def close(self):
        if not self.closing:
            pkt = self.ostream.makeNextPacket(self.connId, payload=b"", isFin=True)
            self._send(pkt)
        self.closing = True


    def isClosed(self):
        return self.ostream.state == State.CLOSED
