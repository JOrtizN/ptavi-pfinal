#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import time
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

class UserAgent(ContentHandler):
    """Sacar puertos e ips. """
    def __init__(self):
        """Diccionario"""
        self.diccConfig = {"account":["username", "passwd"],
                              "uaserver": ["ip","puerto"],
                              "rtpaudio":["puerto"],
                              "regproxy":["ip","puerto"],
                              "log": ["path"],
                              "audio": ["path"],
                              "server": ["name","ip","puerto"],
                              "database":["path", "passwdpath"]}
        self.Config = {}

    def startElement(self, name, attrs):

        if name in self.diccConfig:

            for info in self.diccConfig[name]:
                self.Config[name + '_' + info] = attrs.get(info, "")

    def get_tags(self):
        return self.Config

    def fich_log(self, log_path, evento, mensaje, ip, port):

        hora = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
        user = ip + ":" + str(port)
        fich = open(log_path, "a")
        m_log = hora + " " + evento

        if evento == "Sent":
            mensaje = mensaje.replace("\r\n", " ")
            m_log += " to " + user + ": " + mensaje + "\r\n"
        elif evento == "Received":
            mensaje = mensaje.replace("\r\n", " ")
            m_log += " from " + user + ": " + mensaje + "\r\n"
        elif evento == "Starting":
            m_log += "...\r\n"
        elif evento == "Finishing":
            m_log += ".\r\n"
        elif evento == "Error":
            mensaje = mensaje.replace("\r\n", " ")
            m_log += ": " + mensaje + "\r\n"

        fich.write(m_log)
        fich.close()


if __name__ == "__main__":

    parser = make_parser()
    sHandler = UserAgent()
    parser.setContentHandler(sHandler)
    parser.parse(open(ua))
    Config = sHandler.get_tags()
    #print(Config['account_username'])
