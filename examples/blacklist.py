from datetime import timedelta

import simplekv
import simplekv.memory
from flask import Flask, request, jsonify

from flask_jwt_extended import JWTManager, jwt_required, \
    get_jwt_identity, revoke_token, unrevoke_token, \
    get_stored_tokens, get_all_stored_tokens, create_access_token, \
    create_refresh_token, jwt_refresh_token_required

# Setup flask
app = Flask(__name__)
app.secret_key = 'super-secret'

# Configure access token expires time
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=5)

# Enable and configure the JWT blacklist / token revoke. We are using an in
# memory store for this example. In production, you should use something
# else (csuch as redis, memcached, sqlalchemy). See here for options:
# http://pythonhosted.org/simplekv/
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_STORE'] = simplekv.memory.DictStore()
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = 'refresh'

jwt = JWTManager(app)


@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if username != 'test' and password != 'test':
        return jsonify({"msg": "Bad username or password"}), 401

    ret = {
        'access_token': create_access_token(identity=username),
        'refresh_token': create_refresh_token(identity=username)
    }
    return jsonify(ret), 200


@app.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    ret = {
        'access_token': create_access_token(identity=current_user)
    }
    return jsonify(ret), 200


# Endpoint for listing tokens that have the same identity as you
@app.route('/auth/tokens', methods=['GET'])
@jwt_required
def list_identity_tokens():
    username = get_jwt_identity()
    return jsonify(get_stored_tokens(username)), 200


# Endpoint for listing all tokens. In your app, you should either not expose
# this, or put some addition security on top of it so only trusted users,
# (administrators, etc) can access it
@app.route('/auth/all-tokens')
def list_all_tokens():
    return jsonify(get_all_stored_tokens()), 200


# Endpoint for revoking a token
@app.route('/auth/tokens/revoke/<string:jti>', methods=['PUT'])
@jwt_required
def change_jwt_revoke_state(jti):
    try:
        revoke_token(jti)
        return jsonify({"msg": "Token successfully revoked"}), 200
    except KeyError:
        return jsonify({'msg': 'Token not foun'}), 404


# Endpoint for un-revoking a token
@app.route('/auth/tokens/unrevoke/<string:jti>', methods=['PUT'])
@jwt_required
def change_jwt_revoke_state(jti):
    try:
        unrevoke_token(jti)
        return jsonify({"msg": "Token successfully unrevoked"}), 200
    except KeyError:
        return jsonify({'msg': 'Token not foun'}), 404


@app.route('/protected', methods=['GET'])
@jwt_required
def protected():
    return jsonify({'hello': 'world'})

if __name__ == '__main__':
    app.run()
