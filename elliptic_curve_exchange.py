import os
import sys
from Crypto.Cipher import AES # https://www.dlitz.net/software/pycrypto/
import socket
import argparse
import random
import json
import math

prime_factors_global = []

def main(args):
    parse = argparse.ArgumentParser()
    parse.add_argument('-s', '--isServer', type = int)
    parse.add_argument('-i', '--ip', type = str)
    parse.add_argument('-p', '--port', type = int, required = True)
    parse.add_argument('-size', '--pSize', type = int, default = 16)
    args = parse.parse_args()
    isServer = args.isServer
    ip = args.ip
    port = args.port
    pSize = args.pSize
    if isServer == 0:
        start_server(port, pSize)
    else:
        connect_to_server(ip, port)

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
            a, b = build_curve(10)
            print('Using curve y^2 = x^3 + ' + str(a) + 'x + ' + str(b))
            # find an alpha that is in the curve
            alphX = random.randrange(-20, 20)
            alphY = 0
            while True:
                z = get_z(alphX, a, b, p)
                if z != -1:
                    alphY = int(math.sqrt(z))
                    break
                else:
                    alphX = alphX + 1;
            print('Chose alpha = (' + str(alphX) + ', ' + str(alphY) + ')')
            privKey = random.randrange(1, p - 1)
            print('Private key is ' + str(privKey))
            aux_base = random.randrange(1, 20)
            print('Auxilary base is ' + str(aux_base))
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
            json_aes_key = connection.recv(999999999)
            aes_key = json.loads(json_aes_key)
            AESkey = decrypt(aes_key['y1X'], aes_key['y1Y'], aes_key['coords'], a, privKey, aux_base)
            
            print('Key is ' + str(AESkey))
            cipher = AES.new(str(AESkey))
            msg = connection.recv(128)
            msg = cipher.decrypt(msg)
            print('Final Message : ' + msg)
            msg = cipher.encrypt('1111111111111111')
            connection.send(msg)
            break

def decrypt(y1X, y1Y, coords, a, privKey, aux_base):
    key = ''
    for point in coords:
        print(str(point['x']) + ' ' + str(point['y']))
        ax, ay = curve_dot(y1X, y1Y, a, privKey)
        #need inverse of y1?
        x, y = curve_add(point['x'], point['y'], ax, -ay)
        #check if still int
        m = (x - 1) / aux_base
        key = key + str(int(m))
    return int(key)
        
def curve_dot(x, y, a, q):
    # q(x,y)
    for i in xrange(q):
        lam = calc_lambda(x,y,a)
        x_r = (lam ** 2)
        x_r -= 2 * x
        y_r = lam * (x - x_r)
        y_r -= y
        x = x_r
        y = y_r
    return x, y

def curve_add(px, py, qx, qy):
    lam = qy - py
    lam /= qx - px
    x_r = x_r = (lam ** 2)
    x_r -= (px + qx)
    y_r = lam * (px - x_r)
    y_r -= py
    return x_r, y_r
        
# https://en.wikipedia.org/wiki/Elliptic_curve_point_multiplication#Point_doubling
def calc_lambda(x, y, a):
    top = 3 * (x ** 2) + a
    return top / (2 * y)

def connect_to_server(ip, port):
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect((ip, port))
    clientsocket.send('hello')
    json_pub_key = clientsocket.recv(256)
    public_key = json.loads(json_pub_key)
    k = random.randrange(1, 20)
    y1X, y1Y = curve_dot(public_key['alphX'], public_key['alphY'], public_key['a'], k)
    y2X, y2Y = curve_dot(public_key['betaX'], public_key['betaY'], public_key['a'] , k)
    AESkey = random.randrange(1000000000000000, 9999999999999999)
    str_AESkey = str(AESkey)
    print('Key = ' + str_AESkey)
    #koblitz each character
    encoded_AESkey = [] # List of dicts that have x and y as keys
    for char in str_AESkey:
        x, y = koblitz(public_key['a'], public_key['b'], public_key['p'], int(char), public_key['aux_base'])
        print(str(x) + ' ' + str(y))
        coords = dict()
        coords['x'], coords['y'] = curve_add(x, y, y2X, y2Y)
        encoded_AESkey.append(coords)
    AES_message = dict()
    AES_message['y1X'] = y1X
    AES_message['y1Y'] = y1Y
    AES_message['coords'] = encoded_AESkey
    clientsocket.send(json.dumps(AES_message))
    cipher = AES.new(str_AESkey)
    msg = cipher.encrypt('1111111111111111')
    clientsocket.send(msg)
    msg = clientsocket.recv(128)
    msg = cipher.decrypt(msg)
    print('Response : ' + msg)
    
def koblitz(a, b, p, m, k):
    i = 1
    while True:
        x = m * k + i
        z = get_z(x, a, b, p)
        if (z != -1):
            return (x, math.sqrt(z))
        else:
            i = i + 1
 
#calculates z value, returns -1 if not valid
def get_z(x, a, b, p):
    z = (x**3) + (a*x) + b
    z = z % p
    z1 = z**((p-1)/2) % p
    if (z1 == 1):
        return z
    else:
        return -1

def build_curve(p):
    while True:
        a = random.randrange(1, p - 1)
        b = random.randrange(1, p - 1)
        test =  4*(a**3) + 27*(b**2)
        if (test % p) != 0:
            return a, b
    
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
            #test = alph ** exp
            test = 0
            test = alph
            for i in xrange(exp):
                test = (test * alph) % p
            if (test) == 1:
                found = False
                print('non-generator')
                break
        if found:
           print('Generator found')
           return alph
    return 0

#Find all prime factors of n
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
    
    
if __name__ == '__main__':
    main(sys.argv[1:])
