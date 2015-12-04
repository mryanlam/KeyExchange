import os
import sys
import Crypto # https://www.dlitz.net/software/pycrypto/
import socket
import argparse
import random
import json
import math

def main(args):
    parse = argparse.ArgumentParser()
    parse.add_argument('-s', '--isServer', type = int)
    parse.add_argument('-i', '--ip', type = str)
    parse.add_argument('-p', '--port', type = int, required = True)
    parse.add_argument('-s', '--pSize', type = int, default = 64)
    parse.add_argument('-k', '--keySize', type = int, default = 32)
    
    args = parse.parse_args()
    isServer = args.isServer
    ip = args.ip
    port = args.port
    pSize = args.pSize
    keySize = args.keySize
    if isServer == 0:
        start_server(port, pSize)
    else:
        connect_to_server(ip, port, keySize)

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
            a, b = build_curve()
            print('Using curve y^2 = x^3 + ' + str(a) + 'x + ' + str(b))
            # find an alpha that is in the curve, may need to modify to use koblitz
            alphX = generator(p)
            alphY = 0
            while true:
                z = get_z(alphX, a, b, p)
                if z != -1:
                    alphY = math.sqrt(z)
                    break
                else:
                    alphX++;
            print('Chose alpha = (' + str(alphX) + ', ' + str(alphY) + ')')
            privKey = random.randrange(1, p - 1)
            print('Private key is ' + str(privKey)
            aux_base = random.randrange(1, 20)
            print('Auxilary base is ' + str(aux_base)
            betaX, betaY = curve_dot(alphX, alphY, a, privKey)
            print('Beta = (' + str(betaX) + ', ' + str(betaY) + ')')
            public_key = dict()
            public_key['alphX'] = alphX
            public_key['alphY'] = alphY
            public_key['betaX'] = betaX
            public_key['betaY'] = betaY
            public_key['a'] = a
            public_key['b'] = b
            public_key['p'] = p
            public_key['aux_base'] = aux_base
            json_pub_key = json.dumps(public_key)
            connection.send(json_pub_key)
            json_aes_key = connection.recv(128)
            aes_key = json.loads(json_aes_key)
            AESkey = decrypt(aes_key['y1X'], aes_key['y1Y'], aes_key['coords'], a, privKey, aux_base)
            print('Key is ' + str(AESkey))
            #DECRYPT KEY
            break

def decrypt(y1X, y1Y, coords, a, privKey, aux_base):
    key = ''
    for point in xrange(coords):
        x, y = curve_dot(y1X, y1Y, a, privKey)
        #need inverse of y1?
        x, y = curve_add(point['x'], point['y'], x, y)
        #check if still int
        m = (x - 1) / aux_base
        key = key + str(m)
    return int(key)
        
def curve_dot(x, y, a, q):
    # q(x,y)
    for i in xrange(q):
        lam = calc_lambda(x,y,a)
        x_r = (lam ** 2)
        x_r -= 2 * x
        y_r = lam * (x_r - x)
        y_r -= y
        x = x_r
        y = y_r
    return x, y

def curve_add(px, py, qx, qy):
    lam = qy - py
    lam /= qx - px
    x_r = x_r = (lam ** 2)
    x_r -= 2 * x
    y_r = lam * (x_r - x)
    y_r -= y
    return x_r, y_r
        
# https://en.wikipedia.org/wiki/Elliptic_curve_point_multiplication#Point_doubling
def calc_lambda(x, y, a):
    top = 3 * (x ** 2) + a
    return top / (2 * y)

def connect_to_server(ip, port, keySize):
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect((ip, port))
    clientsocket.send('hello')
    json_pub_key = clientsocket.recv(128)
    public_key = json.loads(json_pub_key)
    k = random.randrange(1, public_key['p'] - 1)
    y1X, y1Y = curve_dot(public_key['alphX'], public_key['alphY'], k)
    y2X, y1Y = curve_dot(public_key['betaX'], public_key['betaY'], k)
    AESkey = random.getrandbits(keySize)
    str_AESkey = str(AESkey)
    print('Key = ' + str_AESkey)
    #koblitz each character
    encoded_AESkey = [] # List of dicts that have x and y as keys
    for char in str_AESkey:
        x, y = koblitz(public_key['a'], public_key['b'], public_key['p'], char, public_key['aux_base'])
        coords = dict()
        coords['x'], coords['y'] = curve_add(x, y, y2X, y2Y)
        encoded_AESkey.append(coords)
    json_encoded_AES = json.loads(encoded_AESkey)
    AES_message = dict()
    AES_message['y1X'] = y1X
    AES_message['y1Y'] = y1Y
    AES_message['coords'] = coords
    clientsocket.send(json.dumps(AES_message))
    
def koblitz(a, b, p, m, k):
    i = 1
    while true:
        x = m*k + i
        z = get_z(x, a, b, p)
        if (z != -i):
            return (x, math.sqrt(z))
        else:
            i++
    

def get_z(x, a, b, p):
    z = (x**3) + (a*x) + b
    z = z % p
    z1 = z**((p-1)/2)
    if (z1 == 1):
        return z
    else:
        return -1

def build_curve(p):
    while true:
        a = random.randrange(1, p - 1)
        b = random.randrange(1, p - 1)
        test =  4*(a**3) + 27*(b**2)
        if (test % p) != 0:
            return a, b
    
#Find Generator
def generator(p):
    k = p -1
    factors = []
    factors = gather_prime_factors(k, factors)
    #factors = prime_factors(k)
    while True:
        alph = random.randrange(1, p)
        print('Testing genrator ' + str(alph))
        found = True   
        for a in factors:
            print('Testing ' + str(a))
            # make sure int?
            exp = k / a
            test = alph**exp
            if (exp % p) == 1:
                found = False
                break
        if found:
           return alph
    return 0

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
    
# Gathers prime factors in m    
def gather_prime_factors(m, factors):
    print('gathering prime factors...')
    #factors = []
    i = 100;
    d = -1
    while result < 0:
        d = polar_alg(m, b)
        b = b + 1
    c = m / d
    factors = check(d, factors)
    factors = check(c, factors)
    return factors

def check(n, factors):
    if RabinMiller(n):
        factors.append(n)
        print('found factor ' + str(n))
    else:
        factors = gather_prime_factors(n, factors)
    return factors
    
def polar_alg(m, b):
    a = 2
    for j in xrange(2, b):
        a = (a**j) % m
    d = gcd(a - 1, m)
    if (1 < d) and (d < m):
        return d
    else:
        return -1

# y is bigger factor        
def gcd(x, y):
    r = 0
    while (x > 0):
        r = y % x
        y = x
        x = r
    return r
    
if __name__ == '__main__':
    main(sys.argv[1:])
