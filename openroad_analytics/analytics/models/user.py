from flask import abort, Response
from statemachine import State, StateMachine



class User:
    """
    Represents the User model configuration for the analytics service.

    Attributes:
        model (dict): Configuration dictionary specifying:
            - datasource (dict): Source information for the user data.
            - auth_field (None): Field used for authentication (currently None).
            - url (str): Endpoint URL for the user resource.
            - schema (dict): Schema definition for the user resource.
            - resource_methods (list): Allowed HTTP methods for the resource endpoint.
            - item_methods (list): Allowed HTTP methods for individual user items.
    """


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


