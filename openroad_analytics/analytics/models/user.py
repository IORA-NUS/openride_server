from flask import abort, Response
from statemachine import State, StateMachine



class User:


    model = {
        'datasource': {
            'source': 'user',
        },
        'auth_field': None,
        'url': 'user',
        'schema': {},

        'resource_methods': ['GET'],
        'item_methods': ['GET', 'PATCH'],
    }

    # registration_model = {
    #     'datasource': {
    #         'source': 'user',
    #     },
    #     'schema': {},
    #     'resource_methods': ['GET', 'POST'],
    #     'internal_resource': True
    # }


