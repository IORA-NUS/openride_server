from flask import abort, Response
from statemachine import State, StateMachine

from api.state_machine import UserStateMachine
# from api.utils import Status


# class UserStates(StateMachine):
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
            'allowed': [s.identifier for s in UserStateMachine().states],
            'default': UserStateMachine().current_state.identifier,
            'required': True,
            'readonly': True
        },
        'transition': {
            'type': 'string',
            'allowed': [t.identifier for t in UserStateMachine().transitions],
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


