#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Clase (y programa principal) para un servidor de eco en UDP simple."""

import socketserver
import socket
import sys
import json
import time
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from useragent import UserAgent
import hashlib
import random


class SIPRegisterHandler(socketserver.DatagramRequestHandler):
    """Echo server class."""

    dicc_registers = {}
    #inviteds = []

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
        line = self.rfile.read()
        if not line:
            pass
        mensaje.append(line.decode('utf-8'))
        lines = " ".join(mensaje)
        mensaje = " ".join(mensaje).split()
        print("STR¿?¿?¿?¿?LINES", lines)
        print("LLEGA:", mensaje, len(mensaje))
        if (mensaje[0] != "REGISTER" and mensaje[0] != "INVITE" and mensaje[0] != "BYE"):
            self.wfile.write(b"Solo contemplamos la opcion REGISTER e INVITE")
            #print("MENSAJE", mensaje)
        if mensaje[0] == "REGISTER":
            ip = mensaje[1].split(":")[1]
            port = mensaje[1].split(":")[2]
            self.json2registered()
            print("ver longitud:", mensaje, len(mensaje))
            if len(mensaje) == 6:
                nonce = random.randint(0,10**15)
                if ip in self.dicc_users:
                    print("Usuario en clientes")
                    #self.dicc_registers[ip] = [IP, PORT]
                    send_nonce = ("SIP/2.0 401 Unauthorized " + "WWW Authenticate: Digest nonce=\"" + str(nonce) + "\"\r\n")
                    self.wfile.write(bytes(send_nonce,'utf-8'))

                else:
                    print("Usuario no encontrado")
                    self.wfile.write(b"SIP/2.0 404 User Not Found\r\n\r\n")
            else:
                if ip in self.dicc_users:
                    self.wfile.write(b"SIP/2.0 200 OK \r\n\r\n")
                    self.dicc_registers[ip] = [IP, port]
                    try:
                        psw = mensaje[-1].split("=")[-1]
                        psw = psw.split("\"")[1]
                        h = hashlib.sha224(bytes(self.dicc_users[ip], 'utf-8'))
                        #h.update(bytes(self.dicc_users[ip]), 'utf-8')
                        h.update(bytes(str(random.randint(0,10**15)), 'utf-8'))
                        newpsw = h.hexdigest()
                    #elif (mensaje[2] != '0\r\n'):
                        if newpsw == psw:
                            reg_date = time.time() + float(mensaje[2])
                            reg_date = time.strftime('%Y-%m-%d %H:%M:%S',
                                                          time.gmtime(reg_date))
                            now_date = time.strftime('%Y-%m-%d %H:%M:%S',
                                                     time.gmtime(time.time()))
                            self.dicc_registers[ip].append(reg_date)
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
                    except IndexError:
                        pass
                    if (mensaje[4] == '0'):
                        #print("CERO!BORRA")
                        if ip in self.dicc_registers:
                            del self.dicc_registers[ip]
                        else:
                            pass
        elif mensaje[0] == "INVITE":
            #self.inviteds.append(mensaje[1].split(":")[1])
            #print(self.inviteds)
            user = mensaje[1].split(":")[1]
            if user in self.dicc_registers:
                #print(self.dicc_registers[user], line)
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
                    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    IP = (self.dicc_registers[user][0])
                    PORT = int(self.dicc_registers[user][1])
                    my_socket.connect((IP, PORT))
                    my_socket.send(bytes(line.decode('utf-8'), 'utf-8'))
                    print("envidado a server", line.decode('utf-8'))
                    try:
                        reciv = my_socket.recv(1024)
                        r_dec = reciv.decode('utf-8').split()
                        print(r_dec)
                        if r_dec[1] and "100" and r_dec[4] == "180" and r_dec[7] == "200":
                            print("si que llega")
                            self.wfile.write(reciv)
                    except:
                        print("no escucha")
                #del self.dicc_registers[user]
                    #self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
        elif mensaje[0] == "BYE":
            #self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
            user = mensaje[1].split(":")[1]
            if user in self.dicc_registers:
                #print(self.dicc_registers[user], line)
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
                    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    IP = (self.dicc_registers[user][0])
                    PORT = int(self.dicc_registers[user][1])
                    my_socket.connect((IP, PORT))
                    my_socket.send(line)
                    print("envidado a server")
                    try:
                        reciv = my_socket.recv(1024)
                        r_dec = reciv.decode('utf-8').split()
                        print(r_dec)
                        if r_dec[1] == "200":
                            print("si que llega")
                            self.wfile.write(reciv)
                            #del self.dicc_registers[user]
                    except:
                        print("no escucha")
                #print("Registro de clientes:", self.dicc_registers)
        elif mensaje[0] == "ACK":
            user = mensaje[1].split(":")[1]
            print("ACK hacer lo que invite!!")
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
                my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                IP = (self.dicc_registers[user][0])
                PORT = int(self.dicc_registers[user][1])
                my_socket.connect((IP, PORT))
                my_socket.send(line)
                try:
                    reciv = my_socket.recv(1024)
                    r_dec = reciv.decode('utf-8').split()
                    #print(reciv)
                    self.wfile.write(reciv)
                except:
                    print("no escucha")
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
