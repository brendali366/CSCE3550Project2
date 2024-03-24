#Brenda Li
#CSCE 3550 PROJECT 2

from flask import Flask, request, jsonify, make_response, render_template, session
import jwt
from datetime import datetime, timedelta #for expire time
from cryptography.hazmat.primitives.asymmetric import rsa #for creating rsa
from cryptography.hazmat.primitives import serialization #for encoding
from cryptography.hazmat.backends import default_backend #for initializing backend OpenSSL
import base64
import json

import sqlite3  #in order to use SQLite you need to import sqlite3

app = Flask(__name__)



#the file name to the database is totally_not_my_privateKeys
fileName = 'totally_not_my_privateKeys.db'

###########################################

# to connect to or create database: fileName (totally_not_my_privateKeys.db)
# used for storing private keys
conn = sqlite3.connect(fileName)

# create a cursor object
# by creating a cursor object it allows to sendn SQL commands to DB
cursor = conn.cursor()

# Define table schema. given execution command
cursor.execute('''CREATE TABLE IF NOT EXISTS keys(
kid INTEGER PRIMARY KEY AUTOINCREMENT,
key BLOB NOT NULL,
exp INTEGER NOT NULL
)''')
               


conn.commit() #saves changes to db
conn.close()


#Generate RSA Keys with public and private

private_key = rsa.generate_private_key(
    public_exponent = 65537, # common exponent to use (largest known Fermat prime)
    key_size = 2048, #2048 bit for RSA Key
    backend = default_backend()
)
public_key = private_key.public_key()

def encode_to_base64url(pub_key):
    #takes the input and converts it to bytes using the big-endian byte order
    value_bytes = pub_key.to_bytes((pub_key.bit_length() + 7) // 8, 'big')
    return jwt.utils.base64url_encode(value_bytes).decode('utf-8') #from bytes to base64 anddecode utf-

#pass n and e to function for base64
n = encode_to_base64url(public_key.public_numbers().n) 
e = encode_to_base64url(public_key.public_numbers().e)



# encrypts private key in PEM
encrypted_private_key = private_key.private_bytes(
encoding = serialization.Encoding.PEM,
format = serialization.PrivateFormat.PKCS8,
encryption_algorithm=serialization.NoEncryption()
)

#public key in PEM
public_key = private_key.public_key().public_bytes(
encoding = serialization.Encoding.PEM,
format = serialization.PublicFormat.SubjectPublicKeyInfo 
)


##########################

def add_key(key, exp):
    conn = sqlite3.connect(fileName)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO keys (key, exp) VALUES (?, ?)''', (key, exp))
    conn.commit()
    conn.close()




#if is expired, it will read one of the non expired key

def retrieve_key(is_expired):
    conn = sqlite3.connect(fileName)
    cursor = conn.cursor()
    if is_expired == 'true': #sets expired to false
        expiry_to_use = datetime.utcnow() + timedelta(days=0, hours=-1)
        cursor.execute('''SELECT * FROM keys WHERE exp <= ?''', expiry_to_use)
    else:
        expiry_to_use = datetime.utcnow() + timedelta(days=0, hours=1)
        cursor.execute('''SELECT * FROM keys WHERE exp > ?''', expiry_to_use)
        entry = cursor.fetchone()
        return entry

def retrieve_allKeys():
    expiry_to_use = datetime.utcnow() + timedelta(days=0, hours=1)
    conn = sqlite3.connect(fileName)
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM keys WHERE exp > ?''', expiry_to_use)
    entries = cursor.fetchall()
    conn.close()
    return entries




def create_jwt(is_expired):
    # Auth endpoint handler
    if is_expired == 'true': #sets expired to true
        key_to_use = encrypted_private_key
        kid = 'KEYbum_exp'
        expiry_to_use = datetime.utcnow() + timedelta(days=0, hours=-1) #to show for expiry
        add_key(key_to_use, expiry_to_use)
    else:
        key_to_use = private_key
        kid = 'KEYbum_val'
        expiry_to_use = datetime.utcnow() + timedelta(days=0, hours=1) #to show non expiry
     
    payload = {'exp': expiry_to_use}
    header = {'kid': kid}
    token = jwt.encode(payload,
                       key_to_use, 
                       algorithm='RS256',headers = header)
    #add_key(key_to_use, expiry_to_use)

    return token

def gen_jwks():
    jwk = {
        'keys':[{
            "kid": 'KEYbum_val',
            "kty": "RSA",
            "alg": "RS256",
            "use": "sig",
            "n": n,
            "e": e,  
             }]
    }

    return jwk

###########



@app.route('/')
def home():
    return 'Server is running properly', 200



#This is the '/auth' endpoint that will return token
@app.route('/auth', methods=['POST'])
def auth():
    is_expired = request.args.get('expired')
    token = create_jwt((is_expired))
    return token


#A /auth endpoint that returns an unexpired, signed JWT on a POST request.
#If the “expired” query parameter is present, issue a JWT signed with the expired key pair and the expired expiry.

@app.route('/.well-known/jwks.json', methods = ['GET'])
def get_jwks():
    #keys = retrieve_allKeys()
    return jsonify(gen_jwks())

if __name__ == "__main__":
    # Server set up on Port 8080
    app.run(host = '127.0.0.1', port=8080, debug = True)
    expiry = datetime.utcnow() + timedelta(days=0, hours=-1)
    add_key(private_key, expiry)
    expiry2 = datetime.utcnow() + timedelta(days=0, hours=1)
    add_key(encrypted_private_key, expiry2)
