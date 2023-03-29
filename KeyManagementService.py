from flask import Flask
import Cryptography
import Operations
from helperhttps import CheckContentType, VerifyMacContent

https = Flask(__name__)
cry = Cryptography
db = Operations
generatorName = '/users/<user_id>/devices/<device_id>/keys/generate'
signingName = '/users/<user_id>/devices/<device_id>/keys/sign'
getPuName = '/users/<user_id>/devices/<device_id>/keys/public'
getPrName = '/users/<user_id>/devices/<device_id>/keys/private'
    
# Verify ownership, generate RSA key pair, add to database and then return public key - JSON with key mac-address  
@https.route(generatorName, methods=['POST'])
def GenerateKeysMain(user_id, device_id):
    data = CheckContentType()
    if(data['key_type'] == 'RSA'):
        private_Key, public_Key = cry.RSAKeyGenerator()
        print(public_Key, private_Key)
        return db.AddKeyPairFromDevice(private_Key, public_Key, device_id)
    else:
        return 'Key type not specified'

@https.route(getPrName, methods=['GET'])
def GetPrKeyMain(user_id, device_id):
    return db.GetPrivateKeyFromID(device_id)
    
@https.route(getPuName, methods=['GET'])
def GetPuKeyMain(user_id, device_id):
    return db.GetPublicKeyFromID(device_id)
    
# Verify ownership, sign message with private key in database, hash the message and then return hashed message
@https.route(signingName, methods=['POST'])
def SignMessageMain(user_id, device_id):
    data = CheckContentType()
    if(data):
        privateKey = db.GetPrivateKeyFromID(device_id)
        print('Task succeeded')
        return cry.SignWithPrivateKey(privateKey, data)
    else:
        return 'Task failed'

if __name__ == "__main__":
    https.run(ssl_context='adhoc')
    