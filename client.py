#!/usr/bin/env python3

import sys
import argparse
import socket

import confundo

parser = argparse.ArgumentParser("Parser")
parser.add_argument("host", help="Set Hostname")
parser.add_argument("port", help="Set Port Number", type=int)
parser.add_argument("file", help="Set File Directory")
args = parser.parse_args()

file = open(args.file, "rb")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

conn = confundo.Socket(sock)
try:
    remote = socket.getaddrinfo(args.host, args.port, family=socket.AF_INET, type=socket.SOCK_DGRAM)
except (socket.error, OverflowError) as e:
    sys.stderr.write("ERROR: Invalid hostname or port (%s)\n" % e)
    sock.close()
    sys.exit(1)

(family, type, proto, canonname, sockaddr) = remote[0]

# send "connect" (not fully connected yet)
conn.connect(sockaddr)

while True:
    try:
        (inPacket, fromAddr) = sock.recvfrom(1024)
        # Note in the above, parameter to .recvfrom should be at least MTU+12 (524), but can be anything else larger if we are willing to accept larger packets

        # Process incoming packet
        conn.on_receive(inPacket)

        # Process any retransmissions
        conn.process_retransmissions()

    except socket.error as e:
        # this is the source of timeouts
        isError = conn.on_timeout()
        if isError:
            # on_timout should return True on critical timeout
            sys.stderr.write("ERROR: (%s)\n" % e)
            sys.exit(1)
        if conn.isClosed():
            break

    while file and conn.canSendData():
        data = file.read(confundo.MTU)
        if not data:
            file = None
            break
        conn.send(data)

    if not file and conn.canSendData():
        conn.close()
