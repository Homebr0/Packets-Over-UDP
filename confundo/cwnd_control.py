# -*- Mode: python; py-indent-offset: 4; indent-tabs-mode: nil; coding: utf-8; -*-
# Copyright 2019 Alex Afanasyev
#

from .common import *

class CwndControl:
    '''Interface for the congestio control actions'''

    def __init__(self):
        self.cwnd = 2.0 * MTU
        self.ssthresh = INIT_SSTHRESH

    def on_ack(self, ackedDataLen):
        #slow start
        if self.cwnd < self.ssthresh:
            self.cwnd += 512
        #congestion avoidance
        elif self.cwnd >= self.ssthresh:
            self.cwnd += (512*512)/self.cwnd
        pass

    def on_timeout(self):
        self.ssthresh = self.cwnd / 2
        self.cwnd = 512
        pass

    def __str__(self):
        return f"cwnd:{self.cwnd} ssthreash:{self.ssthresh}"
