#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
from urllib.parse import urlparse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        code = data.split(" ")[1]
        return int(code)

    def get_headers(self,data):
        header = data.split('\r\n\r\n')[0]
        return header

    def get_body(self, data):
        body = data.index("\r\n\r\n")
        return data[body:]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def url_parse(self, url):
        return urlparse(url)

    def GET(self, url, args=None):
        code = 500
        body = ""
        port = 80

        # Parse URL
        url_parsed = self.url_parse(url)

        # Get host and port
        if (":" not in url_parsed.netloc):
            host = url_parsed.netloc
        else:
            host, port = url_parsed.netloc.split(':')
            port = int(port)

        # Check for empty path
        if (url_parsed.path == ""):
            path = "/"
        else:
            path = url_parsed.path

        self.connect(host, port)
        request = "GET {} HTTP/1.1\r\nHost: {}:{}\r\n\r\n".format(path, host, port) 
        self.sendall(request)
        response = self.recvall(self.socket)

        code = int(self.get_code(response))
        body = self.get_body(response)
        self.close()

        return HTTPResponse(code, body)


    
    def POST(self, url, args=None):
        code = 500
        body = ""
        port = 80

        # Parse URL
        url_parsed = self.url_parse(url)

        # Get host and port
        if (":" not in url_parsed.netloc):
            host = url_parsed.netloc
        else:
            host, port = url_parsed.netloc.split(':')
            port = int(port)

        # Check for empty path
        if (url_parsed.path == ""):
            path = "/"
        else:
            path = url_parsed.path

        self.connect(host, port)

        args_params = list()
        if args != None:
            for key in args:
                pair = "{}={}".format(key, args[key]) 
                args_params.append(pair)
        body = "&".join(args_params)

        request = "POST {} HTTP/1.1\r\nHost: {}:{}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length:{}\r\n".format(path, host, port, len(body))
        request += "\r\n"
        request += body
        
        self.sendall(request)
        response = self.recvall(self.socket)

        code = int(self.get_code(response))
        body = self.get_body(response)
        self.close()

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))