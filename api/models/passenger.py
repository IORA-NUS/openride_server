from flask import abort, Response
import json

# from api.utils import Status
# from .waypoint import WaypointEventSchema

from api.lib import WorkflowStateMachine

# from statemachine import State, StateMachine
# from .user import WorkflowStates

# class PassengerStates(StateMachine):
#     ''' '''

#     dormant = State('dormant', initial=True)
#     offline = State('offline')
#     online = State('online')

#     register = dormant.to(offline)
#     deregister = offline.to(dormant)
#     login = offline.to(online)
#     logout = offline.from_(online)




class Passenger:

    settings_schema = {
        'market': { # patience in Seconds
            'type': 'string',
            'required': True,
            'allowed': ['RideHail']
        },
        'patience': { # patience in Seconds
            'type': 'integer',
            'min': 0,
            'required': True,
            'default': 300
        }
    }


    schema = {
        'run_id': {
            'type': 'string',
            'required': True,
        },

        'state': {
            'type': 'string',
            'allowed': [s.identifier for s in WorkflowStateMachine().states],
            'default': WorkflowStateMachine().current_state.identifier,
            'required': True,
            'readonly': True
        },
        'transition': {
            'type': 'string',
            'allowed': [t.identifier for t in WorkflowStateMachine().transitions],
            'required': False,
        },

        'is_busy': {
            'type': 'boolean',
            # 'allowed': [True,],
            'required': False,
            # 'default': False,
            # 'nullable': True
        },

        'settings': {
            'type': 'dict',
            'schema': settings_schema,
            'required': True,
        },

        'sim_clock': {
            'type': 'datetime',
            'required': False
        },
    }

    model = {
        'datasource': {
            'source': 'passenger',
        },
        'url': '<regex("[a-zA-Z0-9_-]*"):run_id>/passenger',
        'schema': schema,
        'mongo_indexes': {
            'state_index': [
                ('run_id', 1),
                ('state', 1)
            ],
            'unique_user_index': (
                [
                    ('run_id', 1),
                    ('user', 1),
                ],
                {'unique': True}
            )
        },
        'resource_methods': ['GET', 'POST'],
        'item_methods': ['GET', 'PATCH']
    }

