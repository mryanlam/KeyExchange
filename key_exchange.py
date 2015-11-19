import os
import sys
import Crypto # https://www.dlitz.net/software/pycrypto/
import socket
import argparse

def main(args):
    parse = argparse.ArgumentParser()
    parse.add_argument('-s', '--isServer', type = int, default = True, required = True)
    parse.add_argument('-i', '--ip', type = str)
    parse.add_argument('-p', '--port', type = int, required = True)
    
    args = parse.parse_args()
    isServer = args.isServer
    ip = args.ip
    port = args.port
   
    if isServer == 0:
        #key stuff
        #p = get_random_prime()
        
        start_server(port)
        
    else:
        connect_to_server(ip, port)

# Listen for a connection (Server)
# http://stackoverflow.com/questions/7749341/very-basic-python-client-socket-example
def start_server(port):
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind(('localhost', port))
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


# p = prime number, a = random value from Zp, alph = generator
# Build key (alph, a, p)

# Key Exchange

# Encrypt with key ElGamal

# Decrypt with key ElGamal

# AES msg exchange
# def secure_message(input):

#Returns a random prime number
def get_random_prime():
    random_generator = Crypto.Random.new().read
    return Crypto.Util.number.getPrime(1024, random_generator)

if __name__ == '__main__':
    main(sys.argv[1:])
