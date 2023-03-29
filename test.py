import argparse
from hashlib import sha256
from ecdsa import SigningKey
from ecdsa.curves import NIST256p
from ecdsa.keys import sigencode_string


def gen_private(file_name):
    print(f"Saving new private key: {file_name}")
    sk = SigningKey.generate(curve=NIST256p)
    with open(file_name, "wb") as sk_file:
        sk_file.write(sk.to_pem())


def read_private(file_name):
    with open(file_name) as f:
        return SigningKey.from_pem(f.read())

def show_public(sk):
    print("key:" + ''.join(format(b, '02X')
                  for b in sk.get_verifying_key().to_string()))


def sign_text(sk, text):
    message = str.encode(text)
    sig = sk.sign(message, hashfunc=sha256, sigencode=sigencode_string)
    print(f"{text}#" + ''.join(format(b, '02X') for b in sig))


parser = argparse.ArgumentParser(description='r-iot signature tool')
parser.add_argument('--file_name', default='priv.pem',
                    help='Private key file name')
parser.add_argument('--gen_key', action='store_true',
                    help='Generate private key file')
parser.add_argument('--show_pub', action='store_true',
                    help='Show public key')
parser.add_argument('--sign', dest='text',
                    help='Sign text')
args = parser.parse_args()

if args.gen_key:
    gen_private(args.file_name)
else:
    sk = read_private(args.file_name)
    if (args.show_pub):
        show_public(sk)
    elif args.text:
        sign_text(sk, args.text)
