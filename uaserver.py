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
        data = " ".join(mensaje)
        mensaje = " ".join(mensaje).split()
        print("A VER!", mensaje, "MENSAJE", len(mensaje))
        method = mensaje[0]
        IP = self.client_address[0]
        PORT = int(self.client_address[1])
        arroba = mensaje[1].find("@") != -1
        fsip = str(mensaje[1].split(":")[0]) == "sip"
        lsip = str(mensaje[2]) == "SIP/2.0"
        #log: recibed from proxy (IP, PORT) line.decode('utf-8')
        sHandler.fich_log(Log, "Received", data, IP, PORT)

        if fsip and arroba and lsip :
            if method not in ['INVITE', 'BYE', 'ACK']:
                self.wfile.write(b'SIP/2.0 405 Method Not Allowed\r\n')
                error = 'SIP/2.0 405 Method Not Allowed\r\n'
                sHandler.fich_log(Log, "Error", error, IP, PORT)
                sHandler.fich_log(Log, "Sent", error, IP, PORT)
                #log: Send to IP PORT proxy

            if method == "INVITE":
                print("El cliente nos manda: " + line.decode('utf-8'))
                #log: Received from proxy IP , PORT
                #sHandler.fich_log(Log, "Received", data, IP, PORT)
                enviar = ("SIP/2.0 100 Trying\r\n\r\n" +
                          "SIP/2.0 180 Ringing\r\n\r\n" +
                          "SIP/2.0 200 OK\r\n\r\n" +
                          "v=0\r\n" + "o=" + Config['account_username'] + " " +
                          Config['uaserver_ip']+ "\r\n" + "s=PracticaFinal\r\n"
                          + "t=0\r\n" + "m=audio " + Config['rtpaudio_puerto'] +
                          " RTP\r\n")

                self.wfile.write(bytes(enviar, 'utf-8'))
                #log: sent to (IP, PORT) proxy
                sHandler.fich_log(Log, "Sent", enviar, IP, PORT)
                user = mensaje[1].split(":")[1]
                ap = str(mensaje[-2])
                aip = mensaje[7]
                #print(ap, aip)
                self.inviteds[user] = [str(aip), ap]
                print(self.inviteds)

                print("Se supone todo enviado")
            elif method == "ACK":
                print("El cliente nos manda " + line.decode('utf-8'))
                #log: Received from (IP, PORT)proxy
                #sHandler.fich_log(Log, "Received", data, IP, PORT)
                f_audio = Config['audio_path']
                user = mensaje[1].split(":")[1]
                p = self.inviteds[user][1]
                ip = self.inviteds[user][0]
                aEjecutar = 'mp32rtp -i ' + ip + ' -p ' + p +' < ' + f_audio
                print("Vamos a ejecutar", aEjecutar)
                os.system(aEjecutar)
                #log: (ip, p) server otro ua
                sHandler.fich_log(Log, "Sent", aEjecutar, ip, p)
                print("Cancion enviada")

            elif method == "BYE":
                print("El cliente se despide: " + line.decode('utf-8'))
                #log: Received from (IP, PORT)proxy
                #sHandler.fich_log(Log, "Received", data, IP, PORT)
                self.wfile.write(b"SIP/2.0 200 OK \r\n\r\n")
                #log: sen to proxy
                sHandler.fich_log(Log, "Sent", "SIP/2.0 200 OK ", IP, PORT)

        else:
            print("SIP/2.0 400 Bad Request\r\n\r\n")
            error = "SIP/2.0 400 Bad Request "
            self.wfile.write(b"SIP/2.0 400 Bad Request\r\n\r\n")
            sHandler.fich_log(Log, "Error", error, IP, PORT)
            sHandler.fich_log(Log, "Sent", error, IP, PORT)
            #log: ERROR + sen to proxyIP PORT



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
    Log = Config["log_path"]
    IP = Config['uaserver_ip']
    PORT = int(Config['uaserver_puerto'])
    serv = socketserver.UDPServer((IP, PORT), EchoHandler)

    sHandler.fich_log(Log, "Starting", "Starting", IP, PORT)
    print("Listening...")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        sHandler.fich_log(Log, "Finishing", "Finishing", IP, PORT)
        print("END SERVER")
