# -*- Mode: python; py-indent-offset: 4; indent-tabs-mode: nil; coding: utf-8; -*-

import sys
import time

from .common import *
from .istream import Istream
from .ostream import Ostream, State
from .packet import Packet


class Socket:
    '''Incomplete socket abstraction for Confundo protocol'''

    def __init__(self, sock, connId=0):
        self.sock = sock
        self.connId = connId
        self.sock.settimeout(0.5)
        self.istream = None
        self.ostream = None

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

        if pkt.isAck and pkt.isSyn:
            self.connId = pkt.connId
            self.ostream.ack(pkt.ackNum, self.connId)
            self.ostream.ackNum = pkt.seqNum + 1
        elif pkt.isAck:
            self.ostream.ack(pkt.ackNum, self.connId)
            self.ostream.ackNum = pkt.seqNum + 1
        if self.ostream.state == State.FIN_WAIT and not pkt.isFin:
            print(self.format_line("DROP", pkt))

    def process_retransmissions(self):

        ###
        ### IMPLEMENT
        ###

        pass

    def on_timeout(self):
        if self.ostream.on_timeout(self.connId):
            return True
        #Reset cwnd and ssthresh values

        return False

    def connect(self, remote):
        self.remote = remote
        self.ostream = Ostream()

        pkt = self.ostream.makeNextPacket(connId=0, payload=b"", isSyn=True)
        self._send(pkt)

    def canSendData(self):
        return self.ostream.canSendNewData()

    def send(self, payload):
        pkt = self.ostream.makeNextPacket(self.connId, payload)
        self._send(pkt)

    def close(self):
        if self.ostream.state == State.OPEN:
            pkt = self.ostream.makeNextPacket(self.connId, payload=b"", isFin=True)
            self._send(pkt)

    def isClosed(self):
        return self.ostream.state == State.CLOSED