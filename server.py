#!/usr/bin/env python3

import sys
import confundo

# Example how to use the provided confundo.Header class
sampleInput = b'\x00\x00\x00*\x00\x00\x00\x00\x00\x00\x00\x02sample-buffer'
print(sampleInput)
print(sampleInput[0:12])

pkt = confundo.Header()
pkt.decode(sampleInput[0:12])

print(pkt.seqNum, pkt.ackNum, pkt.connId, pkt.isAck, pkt.isSyn, pkt.isFin)

if __name__ == '__main__':
    sys.stderr.write("server is not implemented yet\n")
