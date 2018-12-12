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
if (len(sys.argv) == 2):
    UA = sys.argv[1]
else:
    sys.exit("Server MiServidorBigBang listening at port 5555...")

parser = make_parser()
sHandler = UserAgent()
parser.setContentHandler(sHandler)
#parser.parse(open('ua2.xml'))
parser.parse(open('pr.xml'))
Config = sHandler.get_tags()
IP = Config['server_ip']
PORT = int(Config['server_puerto'])

class SIPRegisterHandler(socketserver.DatagramRequestHandler):
    """Echo server class."""

    dicc_registers = {}

    def json2registered(self):
        """Si existe file_json lo pasa a mi diccionario."""
        #try:
        with open('passwords.json', 'r') as file_json:
            self.dicc_users = json.load(file_json)
            print("contraseñas:", self.dicc_users)
        #except FileNotFoundError:
            #print("no found")
        #    pass

    def register2json(self):
        """Convertir a json."""
        json.dump(self.dicc_registers, open('registed.json', 'w'), indent=3)


    def handle(self):
        """handle method of the register."""
        #sacar la ip y eso del dicc users y cuando coincida con lo que entra en el shell entra en el if
        IP = self.client_address[0]
        EXPIRES = self.client_address[1]
        #print("Registro de clientes:")
        for line in self.rfile:
            if (line == b'\r\n'):
                continue
            mensaje = line.decode('utf-8').split(" ")
            try:
                ip = mensaje[1].split(":")[1]
            except:
                pass
            #print(mensaje, ip)
            if (mensaje[0] == "REGISTER"):
                if ip == "julia1@urjc.es" or ip == "julia2@urjc.es":
                    #print("llega register")
                    self.dicc_registers[ip] = [IP]
                    self.wfile.write(b"SIP/2.0 401 Unauthorized\r\n\r\n")
                if (mensaje[2] == '0\r\n'):
                    try:
                        del self.dicc_registers[user]
                    except IndentationError:
                        pass
                if (mensaje[2] != '0\r\n'):
                    register_date = time.time() + float(EXPIRES)
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
                    if self.dicc_registers[register][1] <= now:
                        del_registers.append(register)
                for register in del_registers:
                    del self.dicc_registers[register]
                self.register2json()

        else:
            self.wfile.write(b"Solo contemplamos la opcion REGISTER")
        print("Registro de clientes:", self.dicc_registers)

        #opcion regproxy


if __name__ == "__main__":
    # Listens at localhost ('') port x
    # and calls the EchoHandler class to manage the request
    serv = socketserver.UDPServer((IP, PORT), SIPRegisterHandler)

    print("Lanzando servidor UDP de eco...")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print
