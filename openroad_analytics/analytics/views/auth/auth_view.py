from flask import request, jsonify, Blueprint
from flask import current_app as app
from eve.auth import TokenAuth
from analytics.config import settings

from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)

from analytics.extensions import jwt
from analytics.extensions import pwd_context
from eve.methods.post import post_internal
from eve.methods.get import get_internal

from bson.objectid import ObjectId
from mongoengine.errors import NotUniqueError

registrtion_bp = Blueprint('auth', __name__, url_prefix='/auth')


@registrtion_bp.route('/signup', methods=['POST'])
def signup():
    '''Authenticate user and return token
    '''
    if not request.is_json:
        return jsonify({'msg': 'Missing JSON in request'}), 400

    user_dict = request.json

    user_dict['password'] = pwd_context.hash(user_dict['password'])
    # resp = post_internal('register_user', user_dict)
    resp = post_internal('user', user_dict)
    # print(resp)
    if resp[0].get('_status') == 'ERR':
        return jsonify({'msg': resp[0]}), resp[3]
    else:
        return jsonify({'msg': 'Successfully Registered User'}), resp[3]


@registrtion_bp.route("/login", methods=["POST"])
def login():
    """Authenticate user and return tokens
    ---
    post:
      tags:
        - auth
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                username:
                  type: string
                  example: myuser
                  required: true
                password:
                  type: string
                  example: P4$$w0rd!
                  required: true
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  access_token:
                    type: string
                    example: myaccesstoken
                  refresh_token:
                    type: string
                    example: myrefreshtoken
        400:
          description: bad request
      security: []
    """
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    email = request.json.get("email", None)
    # run_id = request.json.get("run_id", None)
    password = request.json.get("password", None)
    if not email or not password:
        return jsonify({"msg": "Missing email or password"}), 400

    # user = app.data.find_one_raw('register_user', email=email)
    user = app.data.find_one_raw('user', email=email)

    # if user is None or not pwd_context.verify(password, user.password):
    if user is None or not pwd_context.verify(password, user['password']):
        return jsonify({"msg": "Bad credentials"}), 400

    access_token = create_access_token(identity=str(user['_id']))
    refresh_token = create_refresh_token(identity=str(user['_id']))

    ret = {"access_token": access_token, "refresh_token": refresh_token}
    return jsonify(ret), 200


@registrtion_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """Get an access token from a refresh token
    ---
    post:
    tags:
            - auth
    parameters:
            - in: header
            name: Authorization
            required: true
            description: valid refresh token
    responses:
            200:
            content:
                    application/json:
                    schema:
                            type: object
                            properties:
                            access_token:
                                    type: string
                                    example: myaccesstoken
            400:
            description: bad request
            401:
            description: unauthorized
    """
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    ret = {"access_token": access_token}
    # add_token_to_database(access_token, app.config["JWT_IDENTITY_CLAIM"])
    return jsonify(ret), 200


@registrtion_bp.route("/revoke_access", methods=["DELETE"])
@jwt_required()
def revoke_access_token():
    """Revoke an access token
    ---
    delete:
    tags:
            - auth
    responses:
            200:
            content:
                    application/json:
                    schema:
                            type: object
                            properties:
                            message:
                                    type: string
                                    example: token revoked
            400:
            description: bad request
            401:
            description: unauthorized
    """
    jti = get_jwt()["jti"]
    user_identity = get_jwt_identity()
    # revoke_token(jti, user_identity)
    return jsonify({"message": "token revoked"}), 200


@registrtion_bp.route("/revoke_refresh", methods=["DELETE"])
@jwt_required(refresh=True)
def revoke_refresh_token():
    """Revoke a refresh token, used mainly for logout
    ---
    delete:
    tags:
            - auth
    responses:
            200:
            content:
                    application/json:
                    schema:
                            type: object
                            properties:
                            message:
                                    type: string
                                    example: token revoked
            400:
            description: bad request
            401:
            description: unauthorized
    """
    jti = get_jwt()["jti"]
    user_identity = get_jwt_identity()
    # revoke_token(jti, user_identity)
    return jsonify({"message": "token revoked"}), 200


@jwt.user_identity_loader
def user_identity_loader_callback(_id):
    db = app.data.driver.db
    user_resource = db['user']
    # user = app.data.find_one_raw('user', _id=_id)
    lookup = {'_id': ObjectId(_id)}
    user = user_resource.find_one(lookup)
    # print(user)
    # return str(user['_id'])
    return {
        '_id': str(user['_id']),
        'role': user['role']
    }


# # NOTE This makes a DB Call and is needed only if get_current_user() is used ainwhere in the service
# # At the moment It is not needed and hence commenting this section to avoid unnecessary DB Call
# # Is called at every request ouch.
# # https://flask-jwt-extended.readthedocs.io/en/stable/api/#flask_jwt_extended.get_current_user
# @jwt.user_lookup_loader
# def user_loader_callback(header, jwt_dict):
#     ''' '''
#     # user = app.data.find_one_raw(
#     #     'user', _id=jwt_dict[app.config["JWT_IDENTITY_CLAIM"]])
#     db = app.data.driver.db
#     user_resource = db['user']

#     id_payload = jwt_dict[app.config["JWT_IDENTITY_CLAIM"]]
#     _id = id_payload['_id']
#     # role = id_payload['role']
#     lookup = {'_id': ObjectId(id_payload['_id'])}
#     # user = app.data.find_one_raw('user', _id=_id)
#     user = user_resource.find_one(lookup)

#     return user


# @jwt.token_in_blocklist_loader
# def check_if_token_revoked(decoded_token):
#     return is_token_revoked(decoded_token)

class TokenAuth(TokenAuth):
    @jwt_required()
    def check_auth(self, token, allowed_roles, resource, method):
        # """For the purpose of this example the implementation is as simple as
        # possible. A 'real' token should probably contain a hash of the
        # username/password combo, which sould then validated against the account
        # data stored on the DB.
        # """
        # # use Eve's own db driver; no additional connections/resources are used
        # accounts = app.data.driver.db['accounts']
        # return accounts.find_one({'token': token})
        try:
          # # NOTE: IN Simulation world Security can be controlled with token alons.
          # # SO check_auth shall avoid making DB Calls as it is expensive (every request, ouch)
          #   db = app.data.driver.db
          #   user_resource = db['user']

          #   id_payload = get_jwt()[app.config["JWT_IDENTITY_CLAIM"]]

          #   lookup = {'_id': ObjectId(id_payload['_id'])}
          #   if allowed_roles:
          #       lookup['role'] = {'$in': allowed_roles}

          #   user = user_resource.find_one(lookup)

          #   if user['role'] != 'admin':
          #       self.set_request_auth_value(id_payload['_id'])
          #   return user is not None


            id_payload = get_jwt()[app.config["JWT_IDENTITY_CLAIM"]]
            if id_payload['role'] != 'admin':
                self.set_request_auth_value(id_payload['_id'])

            if allowed_roles:
                if not (id_payload['role'] in allowed_roles):
                    return False

            return True

        except Exception as e:
            print(e)
            raise e

