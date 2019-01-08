#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Programa cliente que abre un socket a un servidor."""

import socket
import sys
import os
import hashlib
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from useragent import UserAgent
METHOD = ""

if len(sys.argv) == 4:
    METHOD = sys.argv[2]
    ua = sys.argv[1]
    opc = sys.argv[3]
else:
    sys.exit("Usage: python3 uaclient.py method opcion")

parser = make_parser()
sHandler = UserAgent()
parser.setContentHandler(sHandler)
parser.parse(open(ua))
Config = sHandler.get_tags()

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    if METHOD == "REGISTER":
        print("reerer")
        USER = Config['account_username']
        IP = (Config['regproxy_ip'])
        PORT = int(Config['regproxy_puerto'])
        S_PORT = str(Config['uaserver_puerto'])
        PSW = (Config['account_passwd'])
        my_socket.connect((IP, PORT))
        my_socket.send(bytes(METHOD + " sip:" + USER + ":" + S_PORT + " SIP/2.0\r\n" + "Expires: "
                       + opc + " SIP/2.0\r\n", 'utf-8') + b'\r\n\r\n')
        data = my_socket.recv(1024).decode('utf-8')
        print(data,"meter en el log esto que hago")
        #autenticacion!!!
        r_dec = data.split()
        print(data.split())
        if r_dec[1] == "401":
            print("HOLA")
            h = hashlib.md5()
            nonce = r_dec[-1].split("=")[-1].split("\"")[1]
            h.update(bytes(PSW, 'utf-8'))
            h.update(bytes(nonce, 'utf-8'))
            sm_nonce = (METHOD +" sip:" + USER + ":" + S_PORT + " SIP/2.0\r\n" + "Expires: " + opc +
                        " SIP/2.0\r\n" + "Authorization: " +
                        "Digest responde=\"" + h.hexdigest() + "\"")
            my_socket.send(bytes(sm_nonce, 'utf-8') + b'\r\n\r\n')

    if METHOD == "INVITE":
        print("Enviando invite...")
        USER = Config['account_username']
        IP = (Config['regproxy_ip'])
        S_IP = Config['uaserver_ip']
        PORT = int(Config['regproxy_puerto'])
        AUDIO_PORT = Config['rtpaudio_puerto']
        my_socket.connect((IP, PORT))
        before = (METHOD + " sip:" + opc + " SIP/2.0\r\n" +
                  "Content-Type: application/sdp\r\n")
        my_socket.send(bytes((before + "v=0\r\n" + "o=" +
                              USER + " " + S_IP + "\r\n" + "s=PracticaFinal\r\n"
                              + "t=0\r\n" + "m=audio " + AUDIO_PORT +
                              " RTP\r\n"), 'utf-8'))
        print("INVITE enviado")
        reciv = my_socket.recv(1024)
        r_dec = reciv.decode('utf-8').split()
        print(reciv.decode('utf-8'), "a ver si es:", r_dec)

        try:
            if r_dec[1] and "100" and r_dec[4] == "180" and r_dec[7] == "200":
                print("Send ACK, if you have to wait your request is okey")
                my_socket.send(bytes("ACK" + " sip:" + opc +
                            " SIP/2.0", 'utf-8') + b'\r\n\r\n')
                f_audio = Config['audio_path']
                ap = str(r_dec[-2])
                aip = r_dec[13]
                print(f_audio, ap, aip)
                aEjecutar = 'mp32rtp -i ' + aip + ' -p ' + ap +' < ' + f_audio
                print("Vamos a ejecutar", aEjecutar)
                os.system(aEjecutar)
                print("Cancion enviada")
                reciv = my_socket.recv(1024)
                r_dec = reciv.decode('utf-8').split()
                try:
                    if r_dec[1] == "400" or r_dec[1] == "405":
                        print(reciv.decode('utf-8'))
                    if r_dec[1] == "404":
                        print(reciv.decode('utf-8'))
                except IndexError:
                    pass
        except IndexError:
            pass

    if METHOD == "BYE":
        print("Se quiere despedir")
        IP = (Config['regproxy_ip'])
        PORT = int(Config['regproxy_puerto'])
        my_socket.connect((IP, PORT))
        my_socket.send(bytes((METHOD + " sip:" + opc + " SIP/2.0\r\n"), 'utf-8'))
        reciv = my_socket.recv(1024)
        print("Recibimos:", reciv.decode('utf-8'))

        print("Terminando socket...")

    else:
        print("ni entra")

print("Fin.")
