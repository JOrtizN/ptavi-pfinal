#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Clase (y programa principal) para un servidor de eco en UDP simple."""

import socketserver
import sys
import json
import time
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from useragent import UserAgent


class SIPRegisterHandler(socketserver.DatagramRequestHandler):
    """Echo server class."""

    dicc_registers = {}

    def json2registered(self):
        """Si existe file_json lo pasa a mi diccionario."""
        with open(Config['database_passwdpath'], 'r') as file_json:
            self.dicc_users = json.load(file_json)
            print("contraseñas:", self.dicc_users)

    def register2json(self):
        """Convertir a json."""
        json.dump(self.dicc_registers, open(Config['database_path'], 'w'))


    def handle(self):
        """handle method of the register."""

        IP = self.client_address[0]
        PORT = self.client_address[1]
        mensaje = []
        for line in self.rfile:
            if (line == b'\r\n'):
                continue
            mensaje.append(line.decode('utf-8'))
            mensaje = " ".join(mensaje).split()
        print("LLEGA:", mensaje)
        if (mensaje[0] != "REGISTER" and mensaje[0] != "INVITE" and mensaje[0] != "BYE"):
            self.wfile.write(b"Solo contemplamos la opcion REGISTER e INVITE")
            #print("MENSAJE", mensaje)
        if mensaje[0] == "REGISTER":
            ip = mensaje[1].split(":")[1]
            self.json2registered()
            if ip in self.dicc_users:
                print("Usuario en clientes")
                self.dicc_registers[ip] = [IP, PORT]
                self.wfile.write(b"SIP/2.0 401 Unauthorized\r\n\r\n")
            if (mensaje[2] == '0'):
                #print("CERO!BORRA")
                if ip in self.dicc_registers:
                    del self.dicc_registers[ip]
                else:
                    pass
            elif (mensaje[2] != '0\r\n'):
                register_date = time.time() + float(mensaje[2])
                register_date = time.strftime('%Y-%m-%d %H:%M:%S',
                                              time.gmtime(register_date))
                now_date = time.strftime('%Y-%m-%d %H:%M:%S',
                                         time.gmtime(time.time()))
                self.dicc_registers[ip].append(register_date)
                self.register2json()

            del_registers = []
            now = time.strftime('%Y-%m-%d %H:%M:%S',
                                time.gmtime(time.time()))
            for register in self.dicc_registers:
                if self.dicc_registers[register][2] <= now:
                    del_registers.append(register)
            for register in del_registers:
                del self.dicc_registers[register]
            self.register2json()
        elif mensaje[0] == "INVITE":
            #comprueba si opc esta en los registrados
            #print(mensaje[1].split(":")[1], self.dicc_registers)
            if mensaje[1].split(":")[1] in self.dicc_registers:
                #mandar mensaje tal cual a server
                self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
        elif mensaje[0] == "BYE":
            self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
        print("Registro de clientes:", self.dicc_registers)

        #opcion regproxy para invite mirar  en el dicc_registers


if __name__ == "__main__":
    # Listens at localhost ('') port x
    # and calls the EchoHandler class to manage the request
    if (len(sys.argv) == 2):
        UA = sys.argv[1]
    else:
        sys.exit("Usage: python uaserver.py config")

    parser = make_parser()
    sHandler = UserAgent()
    parser.setContentHandler(sHandler)
    parser.parse(open(UA))
    Config = sHandler.get_tags()
    IP = Config['server_ip']
    PORT = int(Config['server_puerto'])
    serv = socketserver.UDPServer((IP, PORT), SIPRegisterHandler)

    print("Lanzando servidor UDP de eco...")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print
