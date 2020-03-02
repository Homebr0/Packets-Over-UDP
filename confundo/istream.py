# -*- Mode: python; py-indent-offset: 4; indent-tabs-mode: nil; coding: utf-8; -*-

from .common import *

class Istream:
    def __init__(self, seqNum):
        self.seqNum = seqNum
        self.needAck = False

    def on_packet(self, pkt):
        ###
        ### IMPLEMENT
        ###
        pass

    def __str__(self):
        return f"seqNum:{self.seqNum}"
