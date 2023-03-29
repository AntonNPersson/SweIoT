from flask import Flask, request, jsonify
from flask_oauthlib.provider import OAuth2Provider
import Operations
from helperhttps import CheckContentType
from werkzeug.security import check_password_hash

https = Flask(__name__)
https.secret_key = '348578oA'
db = Operations

oauth = OAuth2Provider(https)

loginName = '/login'
authDeviceName = '/administrator/<user_id>/devices/<device_id>/auth'

@https.route(loginName, methods=['POST'])
def loginMain():
    data = CheckContentType()
    username = data.get('username')
    password = data.get('password')
    user = db.GetSpecificFromColumnInTable(value= username, colum='name', table='users')
    if user and check_password_hash(user.password, password):
        return jsonify({'id': user.id})
    else:
        return jsonify({'Error': 'Invalid credentials'})
    
if __name__ == '__main__':
    https.run(ssl_context='adhoc')