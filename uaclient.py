#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Programa cliente que abre un socket a un servidor."""

import socket
import sys
import os
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
METHOD = ""

if len(sys.argv) == 4:
    METHOD = sys.argv[2]
    ua = sys.argv[1]
    opcion = sys.argv[3]
else:
    sys.exit("Usage: python3 uaclient.py method opcion")

    parser = make_parser()
    sHandler = UserAgent()
    parser.setContentHandler(sHandler)
    #parser.parse(open('ua2.xml'))
    parser.parse(open(ua))
    Config = sHandler.get_tags()

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        USER = Config['account_username'].split("@")[0]
        PORT = int(5060)
        my_socket.connect(("", PORT))
        #my_socket.send(bytes(METHOD + " sip:" + USER + "@" + IP +
        #                     " SIP/2.0", 'utf-8') + b'\r\n\r\n')
    except IndexError:
        sys.exit("Usage: Error in -> receiver@IP:SIPport <-")


    if METHOD == "INVITE":

        PROXY_PORT = Config['regproxy_puerto']
        reciv = my_socket.recv(PROXY_PORT)
        r_dec = reciv.decode('utf-8').split()
        print(data.decode('utf-8'))

        if r_dec[1] == "100" and r_dec[4] == "180" and r_dec[7] == "200":
            print("Send ACK, if you have to wait your request is okey")
            my_socket.send(bytes("ACK" + " sip:" + opcion +
                        " SIP/2.0", 'utf-8') + b'\r\n\r\n')
            reciv = my_socket.recv(PROXY_PORT)
            r_dec = data.decode('utf-8').split()
            try:
                if r_dec[1] == "400" or r_dec[1] == "405":
                    print(data.decode('utf-8'))
                except IndexError:
                    pass

        print("Terminando socket...")

    if METHOD == "REGISTER":

print("Fin.")
