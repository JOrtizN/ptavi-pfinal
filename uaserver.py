#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Clase (y programa principal) para un servidor de eco en UDP simple."""

import socketserver
import socket
import sys
import os
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from useragent import UserAgent



class EchoHandler(socketserver.DatagramRequestHandler):
    """Echo server class."""
    inviteds = {}

    def handle(self):
        """Filtrar por métodos."""
        mensaje = []
        line = self.rfile.read()
        if not line:
            pass
        mensaje.append(line.decode('utf-8'))
        mensaje = " ".join(mensaje).split()
        print("A VER!", mensaje, "MENSAJE", len(mensaje))
        method = mensaje[0]
        IP = self.client_address[0]
        PORT = int(self.client_address[1])
        arroba = mensaje[1].find("@") != -1
        fsip = str(mensaje[1].split(":")[0]) == "sip"
        lsip = str(mensaje[2]) == "SIP/2.0"


        if fsip and arroba and lsip :
            if method not in ['INVITE', 'BYE', 'ACK']:
                self.wfile.write(b'SIP/2.0 405 Method Not Allowed\r\n')

            if method == "INVITE":
                print("El cliente nos manda: " + line.decode('utf-8'))
                self.wfile.write(b"SIP/2.0 100 Trying\r\n\r\n")
                self.wfile.write(b"SIP/2.0 180 Ringing\r\n\r\n")
                self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                self.wfile.write(b"Content-Type: application/sdp\r\n\r\n")
                self.wfile.write(bytes(("v=0\r\n" + "o=" +
                                 Config['account_username'] + " " +
                                 Config['uaserver_ip']+ "\r\n" +
                                 "s=PracticaFinal " + "t=0\r\n" + "m=audio "
                                 + Config['rtpaudio_puerto'] + " RTP\r\n"),
                                 "utf-8"))
                user = mensaje[1].split(":")[1]
                ap = str(mensaje[-2])
                aip = mensaje[7]
                #print(ap, aip)
                self.inviteds[user] = [str(aip), ap]
                print(self.inviteds)

                print("Se supone todo enviado")
            elif method == "ACK":
                print("El cliente nos manda " + line.decode('utf-8'))
                f_audio = Config['audio_path']
                user = mensaje[1].split(":")[1]
                p = self.inviteds[user][1]
                ip = self.inviteds[user][0]
                aEjecutar = 'mp32rtp -i ' + ip + ' -p ' + p +' < ' + f_audio
                print("Vamos a ejecutar", aEjecutar)
                os.system(aEjecutar)
                print("Cancion enviada")

            elif method == "BYE":
                print("El cliente se despide: " + line.decode('utf-8'))
                self.wfile.write(b"SIP/2.0 200 OK \r\n\r\n")
                #else:
                #    print("CANCION: ", llega)

        else:
            print("SIP/2.0 400 Bad Request\r\n\r\n")
            self.wfile.write(b"SIP/2.0 400 Bad Request\r\n\r\n")



if __name__ == "__main__":
    # Creamos servidor de eco y escuchamos
    if (len(sys.argv) == 2):
        UA = sys.argv[1]
    else:
        sys.exit("Usage: python3 uaserver.py config")

    parser = make_parser()
    sHandler = UserAgent()
    parser.setContentHandler(sHandler)
    parser.parse(open(UA))
    Config = sHandler.get_tags()
    IP = Config['uaserver_ip']
    PORT = int(Config['uaserver_puerto'])
    serv = socketserver.UDPServer((IP, PORT), EchoHandler)

    print("Listening...")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("END SERVER")
