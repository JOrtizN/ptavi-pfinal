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

    def handle(self):
        """Filtrar por métodos."""
        for line in self.rfile:
            llega = line.decode('utf-8').split(" ")
            method = llega[0]
            IP = self.client_address[0]
            PORT = int(self.client_address[1])

            try:
                arroba = llega[1].find("@") == -1
                fsip = str(llega[1].split(":")[0]) != "sip"
                lsip = str(llega[2]) != "SIP/2.0\r\n"
                if (fsip or arroba or lsip):
                    print("SIP/2.0 400 Bad Request\r\n\r\n")
                    self.wfile.write(b"SIP/2.0 400 Bad Request\r\n\r\n")
                    break
            except IndexError:
                pass

            if len(llega) == 3:
                if method not in ['INVITE', 'BYE', 'ACK']:
                    self.wfile.write(b'SIP/2.0 405 Method Not Allowed\r\n')
                    break

                if method == "INVITE":
                    print("El cliente nos manda: " + line.decode('utf-8'))
                    self.wfile.write(b"SIP/2.0 100 Trying\r\n\r\n")
                    self.wfile.write(b"SIP/2.0 180 Ringing\r\n\r\n")
                    self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                    self.wfile.write(b"Content-Type: application/sdp\r\n\r\n")
                    self.wfile.write(bytes(("v=0\r\n" + "o=" +
                                     Config['account_username'] + " " +
                                     Config['uaserver_ip']+ "\r\n" +
                                     "s=PracticaFinal" + "t=0\r\n" + "m=audio "
                                     + Config['rtpaudio_puerto'] + " RTP\r\n"),
                                     "utf-8"))
                    print("Se supone todo enviado")

                elif method == "ACK":
                    print("El cliente nos manda " + line.decode('utf-8'))
                    fich_audio = Config['audio_path']
                    aEjecutar = 'mp32rtp -i ' + IP + ' -p ' + str(PORT) +' < ' + fich_audio
                    print("Vamos a ejecutar", aEjecutar)
                    os.system(aEjecutar)
                    print("Cancion enviada")

                elif method == "BYE":
                    print("El cliente nos manda " + line.decode('utf-8'))
                    self.wfile.write(b"SIP/2.0 200 OK \r\n\r\n")

            else:
                break


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
    #with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
    #    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #    IPC = (Config['regproxy_ip'])
    #    PORTC = int(Config['regproxy_puerto'])
    #    my_socket.connect((IPC, PORTC))
        #my_socket.send(b"HOLA SERVER")
    IP = Config['uaserver_ip']
    PORT = int(Config['uaserver_puerto'])
    serv = socketserver.UDPServer((IP, PORT), EchoHandler)

    print("Listening...")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("END SERVER")
