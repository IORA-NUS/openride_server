from flask import abort, Response
from statemachine import State, StateMachine

from api.state_machine import UserStateMachine
# from api.utils import Status


# class UserStsates(StateMachine):
#     ''' '''

#     dormant = State('dormant', initial=True)
#     # activation_requested = State('activation_requested')
#     # activation_sent = State('activation_sent')
#     # activation_failed = State('activation_failed')
#     active = State('active')

#     register = dormant.to(active)
#     deregister = active.to(dormant)

# class WorkflowStates(StateMachine):
#     ''' '''

#     dormant = State('dormant', initial=True)
#     offline = State('offline')
#     online = State('online')

#     register = dormant.to(offline)
#     deregister = offline.to(dormant)
#     login = offline.to(online)
#     logout = offline.from_(online)




class User:
    """
    Represents a User model for the OpenRoad platform API.

    Attributes:
        schema (dict): Validation schema for user fields, including email, password, name, role, public_key, state, transition, and sim_clock.
        model (dict): Configuration for the user resource, including datasource, projection, authentication, URL, schema, MongoDB indexes, and allowed resource/item methods.
        registration_model (dict): Configuration for user registration resource, including datasource, schema, allowed resource methods, and internal resource flag.

    Schema Fields:
        email (str): User's email address. Required, unique, minimum length 1.
        password (str): User's password. Required.
        name (dict): User's name, with required first_name and last_name fields (min/max length 1/64).
        role (str): User's role, allowed values are 'admin' or 'client'. Defaults to 'client'.
        public_key (str): User's public key. Required.
        state (str): User's current state, allowed values from UserStateMachine. Required, read-only.
        transition (str): State transition name, allowed values from UserStateMachine. Optional.
        sim_clock (datetime): Simulation clock timestamp. Optional.

    MongoDB Indexes:
        role_index: Index on 'role' field.
        status_index: Index on 'status' field.
        email_index: Unique index on 'email' field.

    Resource Methods:
        model: Supports 'GET' for resource and 'GET', 'PATCH' for items.
        registration_model: Supports 'GET', 'POST' for resource.

    Note:
        Some fields and relationships (e.g., driver, passenger, status) are commented out and not currently active in the schema.
    """
    schema = {
        'email': {
            'type': 'string',
            'minlength': 1,
            # 'maxlength': 256,
            'required': True,
            'unique': True,
        },
        'password': {
            'type': 'string',
            'required': True,
        },
        'name': {
            'type': 'dict',
            'schema': {
                'first_name': {
                    'type': 'string',
                    'minlength': 1,
                    'maxlength': 64,
                    'required': True,
                },
                'last_name': {
                    'type': 'string',
                    'minlength': 1,
                    'maxlength': 64,
                    'required': True,
                },
            }
        },
        # 'role' is a list, and can only contain values from 'allowed'.
        'role': {
            # 'type': 'list',
            'type': 'string',
            'allowed': ['admin', 'client'],
            'default': 'client', #['client'],
            # 'readonly': True,
        },
        'public_key': {
            'type': 'string',
            'required': True,
        },
        # 'status': {
        #     'type': 'string',
        #     'allowed': [e.value for e in list(Status)],
        #     'default': Status.user_created.value
        # },
        'state': {
            'type': 'string',
            'allowed': [s.name for s in UserStateMachine().states],
            'default': UserStateMachine().current_state.name,
            'required': True,
            'readonly': True
        },
        'transition': {
            'type': 'string',
            'allowed': [t.name for t in UserStateMachine().events],
            'required': False,
        },

        # 'driver':{
        #     'type': 'objectid',
        #     'data_relation': {
        #         'resource': 'driver',
        #         'field': 'id'
        #     },
        #     'required': False
        # }

        # driver = ReferenceField('Driver', required=False)
        # passenger = ReferenceField('Passenger', required=False)
        'sim_clock': {
            'type': 'datetime',
            'required': False
        },

    }

    model = {
        'datasource': {
            'source': 'user',
            'projection': {
                'run_id': 1,
                'email': 1,
                'name': 1,
                'role': 1,
                'state': 1
            }
        },
        'auth_field': None,
        'url': 'user',
        'schema': schema,
        'mongo_indexes': {
            'role_index': [
                ('role', 1)
            ],
            'status_index': [
                ('status', 1)
            ],
            'email_index': (
                [
                    ('email', 1)
                ],
                {'unique': True}
            )
        },
        'resource_methods': ['GET'],
        'item_methods': ['GET', 'PATCH'],
    }

    registration_model = {
        'datasource': {
            'source': 'user',
        },
        'schema': schema,
        'resource_methods': ['GET', 'POST'],
        'internal_resource': True
    }


