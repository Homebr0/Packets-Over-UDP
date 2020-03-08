# -*- Mode: python; py-indent-offset: 4; indent-tabs-mode: nil; coding: utf-8; -*-

import sys
import sys
import time

from .common import *
from .istream import Istream
from .ostream import Ostream, State
from .cwnd_control import  CwndControl
from .packet import Packet
import multiprocessing


class Socket:

    def __init__(self, sock, connId=0):
        self.sock = sock
        self.connId = connId
        self.sock.settimeout(0.5)
        self.istream = None
        self.ostream = None
        self.closing = False
        self.closeTime = 0
        self.closingActReceived = False
        self.congestionLength = 0
        self.cwnd_control = CwndControl()
        self.handshakeDone = False

    def format_line(self, command, pkt):
        s = f"{command} {pkt.seqNum} {pkt.ackNum} {pkt.connId} {int(self.ostream.cc.cwnd)} {self.ostream.cc.ssthresh}"
        if pkt.isAck: s = s + " ACK"
        if pkt.isSyn: s = s + " SYN"
        if pkt.isFin: s = s + " FIN"
        if pkt.isDup: s = s + " DUP"
        return s

    def _send(self, packet):
        '''"Private" method to send packet out'''
        #Add new packet to congestion length
        self.congestionLength += packet.payload.__len__()
        self.sock.sendto(packet.encode(), self.remote)
        print(self.format_line("SEND", packet))

    def on_receive(self, buf):
        '''Method that dispatches the received packet'''
        pkt = Packet().decode(buf)
        print(self.format_line("RECV", pkt))
        
        self.ostream.ack(pkt.ackNum, pkt.connId)


        #Logic to check if Syn-Ack has been received, completing the three-way handshake
        
        if not self.handshakeDone and pkt.isSyn and pkt.isAck:
            self.connId = pkt.connId
        elif not self.handshakeDone:            
            print("SYN-ACK Expected")

        #Changes cwnd and ssthresh values depending on ack received
        if not self.closing and pkt.isAck and not pkt.isSyn and not pkt.isFin:
            dataLen = pkt.ackNum - self.ostream.seqNum
            self.cwnd_control.on_ack( dataLen  )
            #Remove length of previous packet from the congestion length
            self.congestionLength -= (dataLen)

        #Appropriately change the seqNum and AckNum only when receiving signal from server
        if pkt.isAck or pkt.isFin or pkt.isSyn:
            seqFromReceive = pkt.seqNum
            ackFromReceive = pkt.ackNum
            
            self.ostream.ackNum = seqFromReceive + 1
            self.ostream.seqNum = ackFromReceive
        

        #Logic if closing has been initiated
        if self.closing:

            if pkt.isAck and not pkt.isFin and not pkt.isSyn:  # Expect packet with ACK flag
                self.closeTime = time.time()
                
                self.ostream.state = State.FIN_WAIT
                self.closingAckReceived = True 
                pass

            elif pkt.isFin and self.closingAckReceived:  #
                newPkt = self.ostream.makeNextPacket(self.connId, payload=b'', isAck=True)
                #print ("sending that ack of fin")
                self._send(newPkt)

            elif not pkt.isAck:
                #print("ERROR: ACK Flag Expected")
                pass
            else:
                pass  # drop any other non-FIN packet
            
        
            



    def process_retransmissions(self):

        ###
        ### IMPLEMENT
        ###

        pass

    def on_timeout(self):
        '''Called every 0.5 seconds if nothing received'''

        if self.ostream.on_timeout(self.connId):
            return True


        #Reset cwnd and ssthresh values
        self.cwnd_control.on_timeout()


        return False

    def connect(self, remote):
        self.remote = remote
        self.ostream = Ostream()
        
        pkt = self.ostream.makeNextPacket(connId=0, ackNum=0, payload=b"", isSyn=True)

        self._send(pkt)

    def canSendData(self):
        return self.ostream.canSendNewData(self.cwnd_control, self.congestionLength)

    def send(self, payload):
        if not self.handshakeDone:
            pkt = self.ostream.makeNextPacket(self.connId, payload, isAck= True)
            self.handshakeDone = True            
        else:
            pkt = self.ostream.makeNextPacket(self.connId, payload, isAck= False)            
        self._send(pkt)

    def close(self):
        if not self.closing:
            pkt = self.ostream.makeNextPacket(self.connId, payload=b"", isFin=True)
            self._send(pkt)            
        self.closing = True        

    def isClosed(self):
        return self.ostream.state == State.CLOSED
