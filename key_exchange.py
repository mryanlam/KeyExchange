import os
import sys
import Crypto # https://www.dlitz.net/software/pycrypto/
import socket
import argparse
import json
import random
import intertools

def main(args):
    parse = argparse.ArgumentParser()
    parse.add_argument('-s', '--isServer', type = int, required = True)
    parse.add_argument('-i', '--ip', type = str)
    parse.add_argument('-p', '--port', type = int, required = True)
    
    args = parse.parse_args()
    isServer = args.isServer
    ip = args.ip
    port = args.port
   
    if isServer == 0:
        start_server(port)
        # Establish Connection
        # Send Public Key Info
        # Recieve Encrypted AES Key
        # Decrypt AES Key
        # Use AES Key for future
        
    else:
        connect_to_server(ip, port)
        # Server Hello
        # Recieve Public Key
        # Generate AES Key and random number K
        # Encrypt AES Key with K using El Gamal
        # Use AES Key for future
        

# Listen for a connection (Server)
# http://stackoverflow.com/questions/7749341/very-basic-python-client-socket-example
def start_server(port):
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((socket.gethostname(), port))
    serversocket.listen(5) # become a server socket, maximum 5 connections
    
    while True:
        connection, address = serversocket.accept()
        buf = connection.recv(64)
        if len(buf) > 0:
            print(buf)
        
            p = 0
            while True:
                #consider changing
                p = random.getrandbits(128)
                if RabinMiller(p):
                    break
            alph = generator(p)
            a = random.randrange(1, p - 1)
            beta = buildkey(alph, a, p)
            public_key = dict()
            public_key[alph] = alph
            public_key[beta] = beta
            public_key[p] = p
            json_pub_key = json.dumps(public_key)
            connection.send(json_pub_key)
            json_aes_key = clientsocket.recv(128)
            aes_key = json.loads(json_aes_key)
            #get encrypted aes key as aes_key
            AESkey = decrypt(aes_key[y1], aes_key[y2], p, alph, beta, a)
            break
     

# Connect to a server (Client)
def connect_to_server(ip, port):
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect((ip, port))
    clientsocket.send('hello')
    json_pub_key = clientsocket.recv(128)

    #get (p, alpha, beta)
    # download json from server and unpack it
    public_key = json.loads(json_pub_key)
    k = random.randrange(1, public_key[p] - 1)
    AESkey = random.getrandbits(128)
    y1 = gety1(public_key[p], public_key[alph], k)
    y2 = gety2(public_key[p], public_key[beta], k, AESkey)
    AES_message = dict()
    AES_message[y1] = y1
    AES_message[y2] = y2
    #send encrypted key to p1
    clientsocket.send(json.dumps(AES_message))

# p = prime number, alph = generator
def buildkey(alph, a, p):
    beta = math.exp(alph, a)
    beta = beta % p
    return beta

# Key Exchange

# Encrypt with key ElGamal
def gety1(p, alph, k):
    k = random.randrange(1, p - 1)
    y1 = math.exp(alph, k)
    y1 = y1 % p
    return y1
    
def gety2(p, beta, k, AESkey):
    y2 = AESkey * math.exp(beta, k)
    y2 = y2 % p
    return y2

# Decrypt with key ElGamal
def decrypt(y1, y2, p, alph, beta, a):
    AESkey = extended_euclid(y1 * a,p) * y2
    AESkey = AESkey % p
    return AESkey

# Calculates the multiplicative inverse
def inverse(a, m):
    g, x, y = extended_euclid(a, m)
    if g == 1:
        return x % m

def extended_euclid(a, b):
    prevx, x = 1, 0; prevy, y = 0, 1
    while b:
        q = a/b
        x, prevx = prevx - q*x, x
        y, prevy = prevy - q*y, y
        a, b = b, a % b
    return a, prevx, prevy

# AES msg exchange
# def secure_message(input):
#Rabin Miller
def RabinMiller(n, k = 7):
    if n < 6: 
        return [False, False, True, True, False, True][n]
    elif n & 1 == 0: 
        return False
    else:
        s, d = 0, n - 1
        while d & 1 == 0:
            s, d = s + 1, d >> 1
        for a in random.sample(xrange(2, min(n - 2, sys.maxint)), min(n - 4, k)):
            x = pow(a, d, n)
            if x != 1 and x + 1 != n:
                for r in xrange(1, s):
                    x = pow(x, 2, n)
                    if x == 1:
                        return False
                    elif x == n - 1:
                        a = 0  
                        break  
                if a:
                    return False  
    return True
      
#Find Generator
def generator(p):
    k = p -1
    
    while True:
        alph = random.randrange(1, p)
        found = True   
        for a in xrange(1, p):
            # make sure int?
            exp = k / a
            test = alph**exp
            if (exp % p) == 1:
                found = False
                break
        if found:
           return alph
    return 0
        

#Returns a random prime number
def get_random_prime():
    random_generator = Crypto.Random.new().read
    return Crypto.Util.number.getPrime(1024, random_generator)

def prime_factors(n):
    i = 2
    factors = []
    while i * i <= n:
        if n % i:
            i += 1
        else:
            n //= i
            factors.append(i)
    if n > 1:
        factors.append(n)
    return factors
if __name__ == '__main__':
    main(sys.argv[1:])
