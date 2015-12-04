import os
import sys
from Crypto.Cipher import AES # https://www.dlitz.net/software/pycrypto/
import socket
import argparse
import json
import math
import random
import fractions

prime_factors_global = []

def main(args):
    parse = argparse.ArgumentParser()
    parse.add_argument('-s', '--isServer', type = int)
    parse.add_argument('-i', '--ip', type = str)
    parse.add_argument('-p', '--port', type = int, required = True)
    parse.add_argument('-size', '--pSize', type = int, default = 16)
    parse.add_argument('-k', '--keySize', type = int, default = 16)
    
    args = parse.parse_args()
    isServer = args.isServer
    ip = args.ip
    port = args.port
    pSize = args.pSize
    keySize = args.keySize
   
    if isServer == 0:
        start_server(port, pSize)
        # Establish Connection
        # Send Public Key Info
        # Recieve Encrypted AES Key
        # Decrypt AES Key
        # Use AES Key for future
        
    else:
        connect_to_server(ip, port, keySize)
        # Server Hello
        # Recieve Public Key
        # Generate AES Key and random number K
        # Encrypt AES Key with K using El Gamal
        # Use AES Key for future
        

# Listen for a connection (Server)
# http://stackoverflow.com/questions/7749341/very-basic-python-client-socket-example
def start_server(port, pSize):
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
                #change p size
                p = random.getrandbits(pSize)
                if RabinMiller(p):
                    print('Found prime ' + str(p))
                    break
            print('gathering prime factors...')
            alph = generator(p)
            a = random.randrange(1, p - 1)
            beta = buildkey(alph, a, p)
            public_key = dict()
            public_key['alph'] = alph
            public_key['beta'] = beta
            public_key['p'] = p
            json_pub_key = json.dumps(public_key)
            connection.send(json_pub_key)
            json_aes_key = connection.recv(128)
            aes_key = json.loads(json_aes_key)
            #get encrypted aes key as aes_key
            aes_key_list = []
            for digit in aes_key['y2']:
                aes_key_list.append(decrypt(aes_key['y1'], digit, p, alph, beta, a))
            AESkey = "".join([str(x) for x in aes_key_list])
            print('p is ' + str(p))
            print('alph is ' + str(alph))
            print('beta is ' + str(beta))
            print('a is ' + str(a))
            print('y1 is ' + str(aes_key['y1']))
            print('key is ' + str(AESkey))
            
            cipher = AES.new(str(AESkey)) # check formating
            msg = connection.recv(64)
            msg = cipher.decrypt(msg)
            print('Final Message : ' + msg)
            msg = cipher.encrypt('This is the response')
            connection.send(msg)
            break
     

# Connect to a server (Client)
def connect_to_server(ip, port, keySize):
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect((ip, port))
    clientsocket.send('hello')
    json_pub_key = clientsocket.recv(128)

    #get (p, alpha, beta)
    # download json from server and unpack it
    public_key = json.loads(json_pub_key)
    k = random.randrange(1, 10) 
    # change AES key size
    AESkey = randomBytes(keySize)
    
    y2_list = []
    for digit in str(AESkey):
        y2_list.append(gety2(public_key['p'], public_key['beta'], k, int(digit)))
    y1 = gety1(public_key['p'], public_key['alph'], k)
    AES_message = dict()
    AES_message['y1'] = y1
    AES_message['y2'] = y2_list
    print('p is ' + str(public_key['p']))
    print('alph is ' + str(public_key['alph']))
    print('beta is ' + str(public_key['beta']))
    print('k is ' + str(k))
    print('y1 is ' + str(y1))
    #send encrypted key to p1
    clientsocket.send(json.dumps(AES_message))
    print('key is ' + str(AESkey))
    print sys.getsizeof(AESkey)
    cipher = AES.new(str(AESkey)) # check formating
    msg = cipher.encrypt('It\'s a secret to everybody')
    clientsocket.send(msg)
    msg = clientsocket.recv(64)
    msg = cipher.decrypt(msg)
    print('Response : ' + msg)

def randomBytes(n):
    bytes = ""
    for i in range(n):
        bytes += str(random.getrandbits(8))
    return bytes
    
# p = prime number, alph = generator
def buildkey(alph, a, p):
    beta = alph**a
    beta = beta % p
    return beta

# Key Exchange

# Encrypt with key ElGamal
def gety1(p, alph, k):
    y1 = alph**k
    y1 = y1 % p
    return y1
    
def gety2(p, beta, k, AESkey):
    print p
    print beta
    print k
    print AESkey
    print "-----"
    y2 = AESkey * (beta**k)
    y2 = y2 % p
    return y2

# Decrypt with key ElGamal
def decrypt(y1, y2, p, alph, beta, a):
    AESkey = inverse(y1**a, p) * y2
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
    #gather_prime_factors(k)
    prime_factors(k)
    while True:
        alph = random.randrange(1, 10)
        print('Testing genrator ' + str(alph))
        found = True   
        for a in prime_factors_global:
            print('Testing ' + str(a))
            # make sure int?
            exp = k / a
            print('exp = ' + str(exp))
            test = alph**exp
            if (test % p) == 1:
                found = False
                print('non-generator')
                break
        if found:
           print('Generator found')
           return alph
    return 0

def prime_factors(n):
    print('gathering prime factors...')
    i = 2
    while i * i <= n:
        if n % i:
            i += 1
        else:
            n //= i
            prime_factors_global.append(i)
            print('found factor ' + str(i))
    if n > 1:
        print('found factor ' + str(i))
        prime_factors_global.append(n)
        

#Returns a random prime number
def get_random_prime():
    random_generator = Crypto.Random.new().read
    return Crypto.Util.number.getPrime(1024, random_generator)


def gather_prime_factors(m):
    #factors = []
    b = 500
    d = -1
    while d < 0:
        d = polar_alg(m, b)
        if ((d == m) or (d == 1)):
            break
        if ((d < 1) or (d > m)):
            b = b + 1
    c = m / d
    check(d)
    check(c)


def check(n):
    if (RabinMiller(n)):
        prime_factors_global.append(n)
        print('found factor ' + str(n))
    elif n != 1:
        gather_prime_factors(n)
    
def polar_alg(m, b):
    a = 2
    for j in xrange(2, b):
        a = (a**j) % m
    print('a = ' + str(a))
    d = fractions.gcd(a - 1, m) #gcd(a - 1, m)
    print('gcd = ' + str(d))
    return d


if __name__ == '__main__':
    main(sys.argv[1:])
