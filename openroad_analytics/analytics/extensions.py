

from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import JWTManager
from flask_cors import CORS, cross_origin
from eve_swagger import get_swagger_blueprint, add_documentation
from analytics.config import settings


jwt = JWTManager()
cors = CORS()
pwd_context = pbkdf2_sha256
swagger = get_swagger_blueprint()
