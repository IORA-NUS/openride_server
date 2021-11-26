from analytics.utils import Env

DEBUG = Env.bool('DEBUG', True)
SECRET_KEY = Env.string('SECRET_KEY', 'changeme')

# If Docker
# MONGODB_HOST = 'host.docker.internal'   # NOTE Works only on Docker for Mac. For linus, see https://stackoverflow.com/questions/31324981/how-to-access-host-port-from-docker-container
# Else
# MONGODB_HOST = '192.168.10.135'   # NOTE Home network
MONGODB_HOST = Env.string('MONGODB_HOST', 'localhost')
MONGODB_PORT = Env.int('MONGODB_PORT', 27017)
MONGODB_NAME = Env.string('MONGODB_NAME', 'OpenRoadDB')
# MONGODB_NAME = Env.string('MONGODB_NAME', 'OpenRoadDB_20211124')

# MONGODB_SETTINGS = [{
#     'db': MONGODB_NAME,
#     'host': MONGODB_HOST,
#     'port': MONGODB_PORT
# }]

SWAGGER_INFO = {
    'title': 'OpenRoad Analytics',
    'version': '0.0.1',
    'description': 'an API description',
    'termsOfService': 'my terms of service',
    'contact': {
        'name': 'iora admin',
        'url': 'http://iora.nus.edu.sg'
    },
    'license': {
        'name': 'BSD',
        'url': 'https://github.com/nicolaiarocci/eve-swagger/blob/master/LICENSE',
    }
}


settings = {
    'DEBUG': DEBUG,
    'SECRET_KEY': SECRET_KEY,
    # 'DATE_FORMAT': r"%Y-%m-%dT%H:%M:%S.%f%Z%z",
    # 'PLOT_STATE_TRANSITIONS': True,

    "JWT_TOKEN_LOCATION": ["headers"],
    "JWT_SECRET_KEY": "super-secret",
    "JWT_ACCESS_TOKEN_EXPIRES": 1000000,
    "JWT_IDENTITY_CLAIM": 'uid',
    "JWT_HEADER_TYPE": 'JWT',

    "ALLOWED_ROLES": ['admin', 'client'],


    # database
    'MONGO_HOST': MONGODB_HOST,
    'MONGO_PORT': MONGODB_PORT,
    'MONGO_DBNAME': MONGODB_NAME,

    # Swagger documentation
    'SWAGGER_INFO': SWAGGER_INFO,

    # important settings
    'AUTH_FIELD': 'user',
    'OPTIMIZE_PAGINATION_FOR_SPEED': True,

    # 'ALLOW_CUSTOM_FIELDS_IN_GEOJSON': True,
    'NORMALIZE_ON_PATCH': False,

}


