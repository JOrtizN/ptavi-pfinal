#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Clase (y programa principal) para un servidor de eco en UDP simple."""

import socketserver
import sys
import json
import time
if (len(sys.argv) == 2):
    PORT = int(sys.argv[1])
else:
    sys.exit("Usage: <PORT>")


class SIPRegisterHandler(socketserver.DatagramRequestHandler):
    """Echo server class."""

    dicc_registers = {}

    def register2json(self):
        """Convertir a json."""
        json.dump(self.dicc_registers, open('registed.json', 'w'), indent=3)

    def json2registered(self):
        """Si existe file_json lo pasa a mi diccionario."""
        try:
            with open('passwords.json', 'r') as file_json:
                self.dicc_users = json.load(file_json)
        except FileNotFoundError:
            pass

    def handle(self):
        """handle method of the server."""
        IP = self.client_address[0]
        PORT = self.client_address[1]
        print("Registro de clientes:")

        for line in self.rfile:
            mensaje = line.decode('utf-8').split(" ")
            if (mensaje[0] == "REGISTER"):
                user = mensaje[1].split(':')[1]
                self.dicc_registers[user] = [IP]
                self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
            elif (mensaje[0] == "EXPIRES:"):
                EXPIRES = mensaje[1].split(':')[-1]
                if (EXPIRES == '0\r\n'):
                    try:
                        del self.dicc_registers[user]
                    except IndentationError:
                        pass

                else:
                    register_date = time.time() + float(EXPIRES)
                    register_date = time.strftime('%Y-%m-%d %H:%M:%S',
                                                  time.gmtime(register_date))
                    now_date = time.strftime('%Y-%m-%d %H:%M:%S',
                                             time.gmtime(time.time()))
                    self.dicc_registers[user].append(register_date)
                    self.register2json()

                del_registers = []
                now = time.strftime('%Y-%m-%d %H:%M:%S',
                                    time.gmtime(time.time()))
                for register in self.dicc_users:
                    #mandar error 401 de autenticacion y despues le dejo registrarse si authentic
                    if self.dicc_registers[register][1] <= now:
                        del_registers.append(register)
                for register in del_registers:
                    del self.dicc_registers[register]
                self.register2json()

            elif (line == b'\r\n'):
                pass

            else:
                self.wfile.write(b"Solo contemplamos la opcion REGISTER")
        print(self.dicc_registers)


if __name__ == "__main__":
    # Listens at localhost ('') port x
    # and calls the EchoHandler class to manage the request
    serv = socketserver.UDPServer(('', PORT), SIPRegisterHandler)

    print("Lanzando servidor UDP de eco...")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print
