import os
import sys
import Crypto # https://www.dlitz.net/software/pycrypto/
import socket
import argparse
import random

def main(args):
    parse = argparse.ArgumentParser()
    parse.add_argument('-s', '--isServer', type = int)
    parse.add_argument('-i', '--ip', type = str)
    parse.add_argument('-p', '--port', type = int, required = True)
    
    args = parse.parse_args()
    isServer = args.isServer
    ip = args.ip
    port = args.port
   
    if isServer == 0:
        start_server(port)
        
    else:
        connect_to_server(ip, port)

def start_server(port):
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((socket.gethostname(), port))
    serversocket.listen(5) # become a server socket, maximum 5 connections
    
    while True:
        connection, address = serversocket.accept()
        buf = connection.recv(64)
        if len(buf) > 0:
            print(buf)
        #Generate p as before
        #Chose a, b
        
        break
        
def connect_to_server(ip, port):
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect((ip, port))
    clientsocket.send('hello')