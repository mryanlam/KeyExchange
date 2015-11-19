import os
import Crypto # https://www.dlitz.net/software/pycrypto/
import socket

def main():
    

# Listen for a connection (Server)
# http://stackoverflow.com/questions/7749341/very-basic-python-client-socket-example
def start_server():
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind(('localhost', 8089))
    serversocket.listen(5) # become a server socket, maximum 5 connections
    while True:
        connection, address = serversocket.accept()
        buf = connection.recv(64)
        if len(buf) > 0:
            print(buf)
            break

# Connect to a server (Client)
def connect_to_server(ip, port):
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect((ip, port))
    clientsocket.send('hello')

# Miller-Rabin Random Prime


# p = prime number, a = random value from Zp, alph = generator
# Build key (alph, a, p)

# Key Exchange

# Encrypt with key ElGamal

# Decrypt with key ElGamal

# AES msg exchange
def secure_message(input):
