#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
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



if __name__ == "__main__":

    parser = make_parser()
    sHandler = UserAgent()
    parser.setContentHandler(sHandler)
    parser.parse(open(ua))
    Config = sHandler.get_tags()
    #print(Config['account_username'])
