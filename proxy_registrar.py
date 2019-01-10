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
        #print("STR¿?¿?¿?¿?LINES", lines)
        #print("LLEGA:", mensaje, len(mensaje))
        if (mensaje[0] != "REGISTER" and mensaje[0] != "INVITE" and mensaje[0]
            != "BYE" and mensaje[0] != "SIP/2.0" and mensaje[0] != "ACK"):
            self.wfile.write(b"SIP/2.0 405 Method Not Allowed\r\n\r\n")
            print("SIP/2.0 405 Method Not Allowed")
            enviar = "SIP/2.0 405 Method Not Allowed "
            sHandler.fich_log(Log, "Sent", enviar, IP, PORT)
            sHandler.fich_log(Log, "Error", enviar, IP, PORT)
            sys.exit(mensaje[0])
           #break
        if mensaje[0] == "REGISTER":
            ip = mensaje[1].split(":")[1]
            port = mensaje[1].split(":")[2]
            self.json2registered()
            print("ver longitud:", mensaje, len(mensaje))
            #LOG Received client_address lines
            data = line.decode('utf-8')
            sHandler.fich_log(Log, "Received", data, IP, PORT)
            if ip in self.dicc_users:
                if len(mensaje) == 6:
                    nonce = random.randint(0,10**15)
                    print("Usuario en clientes")
                    #self.dicc_registers[ip] = [IP, PORT]
                    send_nonce = ("SIP/2.0 401 Unauthorized " +
                                  "WWW Authenticate: Digest nonce=\"" +
                                  str(nonce) + "\"\r\n")
                    self.wfile.write(bytes(send_nonce,'utf-8'))
                    #LOG Sent client_address
                    sHandler.fich_log(Log, "Sent", send_nonce, IP, PORT)

                if len(mensaje) == 9:#if ip in self.dicc_users:
                    self.wfile.write(b"SIP/2.0 200 OK \r\n\r\n")
                    #LOG Sent client_address
                    sHandler.fich_log(Log, "Sent", "SIP/2.0 200 OK ", IP, PORT)
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

                    except IndexError:
                        pass
                    if (mensaje[4] == '0'):
                        #print("CERO!BORRA")
                        if ip in self.dicc_registers:
                            del self.dicc_registers[ip]
                            self.register2json()
                        else:
                            pass
                #if len(mensaje) != 9 or len(mensaje) != 6:
                #    print(mensaje, len(mensaje), "problema de formato BAD REQUEST")
                #    self.wfile.write(b"SIP/2.0 400 Bad Request\r\n\r\n")
                #    enviar = "SIP/2.0 400 Bad Request "
                #    sHandler.fich_log(Log, "Sent", enviar, IP, PORT)
                #    sHandler.fich_log(Log, "Error", enviar, IP, PORT)
            else:
                print("Usuario no encontrado")
                self.wfile.write(b"SIP/2.0 404 User Not Found\r\n\r\n")
                #LOG Sent client_address
                enviar = "SIP/2.0 404 User Not Found "
                sHandler.fich_log(Log, "Sent", enviar, IP, PORT)
                sHandler.fich_log(Log, "Error", enviar, IP, PORT)

        elif mensaje[0] == "INVITE":
            #self.inviteds.append(mensaje[1].split(":")[1])
            #print(self.inviteds)
            #LOG Received client_address
            sHandler.fich_log(Log, "Received", lines, IP, PORT)
            user = mensaje[1].split(":")[1]
            if user in self.dicc_registers:
                #print(self.dicc_registers[user], line)
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
                    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    SIP = (self.dicc_registers[user][0])
                    SPORT = int(self.dicc_registers[user][1])
                    my_socket.connect((SIP, SPORT))
                    enviar = line.decode('utf-8')
                    my_socket.send(bytes(enviar, 'utf-8'))
                    #LOG SENT ip port xml
                    sHandler.fich_log(Log, "Sent", enviar, SIP, SPORT)
                    print("envidado a server", line.decode('utf-8'))
                    try:
                        reciv = my_socket.recv(1024)
                        r_dec = reciv.decode('utf-8').split()
                        data = reciv.decode('utf-8')
                        #sHandler.fich_log(Log, "Received", data, IP, PORT)
                        #LOG Received client_address
                        print(r_dec)
                        if r_dec[1] and "100" and r_dec[4] == "180" and r_dec[7] == "200":
                            sHandler.fich_log(Log, "Received", data, IP, PORT)
                            print("si que llega")
                            self.wfile.write(reciv)
                            #LOG Sent client_address
                            sHandler.fich_log(Log, "Sent", data, IP, PORT)
                    except:
                        print("no escucha")
            else:
                print("Usuario no encontrado")
                self.wfile.write(b"SIP/2.0 404 User Not Found\r\n\r\n")
                error = "SIP/2.0 404 User Not Found\r\n\r\n"
                sHandler.fich_log(Log, "Sent", error, IP, PORT)
                sHandler.fich_log(Log, "Error", error, IP, PORT)
                #del self.dicc_registers[user]
                    #self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
        elif mensaje[0] == "BYE":
            #self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
            user = mensaje[1].split(":")[1]
            #LOG Received client_address
            data = line.decode('utf-8')
            sHandler.fich_log(Log, "Received", data, IP, PORT)
            if user in self.dicc_registers:
                #print(self.dicc_registers[user], line)
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
                    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    SIP = (self.dicc_registers[user][0])
                    SPORT = int(self.dicc_registers[user][1])
                    my_socket.connect((SIP, SPORT))
                    my_socket.send(line)
                    #LOG Sent xml
                    sHandler.fich_log(Log, "Sent", data, SIP, SPORT)
                    print("envidado a server")
                    try:
                        reciv = my_socket.recv(1024)
                        r_dec = reciv.decode('utf-8').split()
                        data = reciv.decode('utf-8')
                        #LOG Received client_address
                        sHandler.fich_log(Log, "Received", data, IP, PORT)
                        print(r_dec)
                        if r_dec[1] == "200":
                            #log Received
                            #sHandler.fich_log(Log, "Received", data, IP, PORT)
                            print("si que llega")
                            self.wfile.write(reciv)
                            #LOG Sent client_address
                            sHandler.fich_log(Log, "Sent", data, IP, PORT)
                            #del self.dicc_registers[user]
                    except:
                        print("no escucha")
                #print("Registro de clientes:", self.dicc_registers)
        elif mensaje[0] == "ACK":
            user = mensaje[1].split(":")[1]
            #LOG Received client_address
            print("LNE!", line)
            data = line.decode('utf-8')
            print(data)
            sHandler.fich_log(Log, "Received", data, IP, PORT)
            print("ACK hacer lo que invite!!")
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
                my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                SIP = (self.dicc_registers[user][0])
                SPORT = int(self.dicc_registers[user][1])
                my_socket.connect((SIP, SPORT))
                my_socket.send(line)
                #LOG SENT xml
                sHandler.fich_log(Log, "Sent", lines, SIP, SPORT)

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
    Log = Config["log_path"]
    IP = Config['server_ip']
    PORT = int(Config['server_puerto'])
    serv = socketserver.UDPServer((IP, PORT), SIPRegisterHandler)
    #LOG! start
    sHandler.fich_log(Log, "Starting", "Starting", IP, PORT)
    print("Lanzando servidor UDP de eco...")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        #LOG Finishing
        sHandler.fich_log(Log, "Finishing", "Finishing", IP, PORT)
