from flask import abort, Response
import json

from api.utils import Status
# from .waypoint import WaypointEventSchema
from api.lib import WorkflowStateMachine

# from statemachine import State, StateMachine
# from .user import WorkflowStates

# class VehicleStates(StateMachine):
#     ''' '''
#     dormant = State('dormant', initial=True)
#     offline = State('offline')
#     online = State('online')

#     register = dormant.to(offline)
#     deregister = offline.to(dormant)
#     login = offline.to(online)
#     logout = online.to(offline)


class Vehicle:

    RegistrationSchema = {
        'num': {
            'type': 'string',
            'minlength': 1,
            'maxlength': 32,
            'required': True,
        },
        'country': {
            'type': 'string',
            'minlength': 1,
            'maxlength': 64,
            'required': True,
        },
        'expiry': {
            'type': 'datetime',
            'required': True,
        }
    }

    schema = {
        'run_id': {
            'type': 'string',
            'required': True,
        },
        # 'user':{
        #     'type': 'objectid',
        #     'data_relation': {
        #         'resource': 'user',
        #         'field': '_id'
        #     },
        #     'required': True,
        #     # 'unique': True,
        #     # # make sure to set auto_add_user=True in the resource def
        # },

        'registration': {
            'type': 'dict',
            'schema': RegistrationSchema,
            'required': True,
        },
        # 'registration_num': {
        #     'type': 'string',
        #     'minlength': 1,
        #     'maxlength': 32,
        #     'required': True,
        # },
        # 'registration_country': {
        #     'type': 'string',
        #     'minlength': 1,
        #     'maxlength': 64,
        #     'required': True,
        # },
        # 'registration_expiry': {
        #     'type': 'datetime',
        #     'required': True,
        # },


        'capacity': {
            'type': 'integer',
            'min': 1,
            'required': True,
        },
        'color': {
            'type': 'string',
        },

        # 'status': {
        #     'type': 'string',
        #     'allowed': [e.value for e in list(Status)],
        #     'default': Status.vehicle_dormant.value,
        #     'required': True,
        # },
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

        'authorised_drivers':{
            'type': 'list',
            # 'unique_in_list': ['id'],
            'schema': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'driver',
                    'field': '_id'
                },
            },
        },

        # 'driver_list':{
        #     'type': 'list',
        #     # 'unique_in_list': ['id'],
        #     'schema': {
        #         'type': 'objectid',
        #         'data_relation': {
        #             'resource': 'driver',
        #             'field': '_id'
        #         },
        #     },
        # },

        # 'active_driver': {
        #     'type': 'objectid',
        #     'data_relation': {
        #         'resource': 'driver',
        #         'field': '_id'
        #     },
        #     'required': False,
        # },

        'sim_clock': {
            'type': 'datetime',
            'required': False
        },

    }

    model = {
        'datasource': {
            'source': 'vehicle',
        },
        'url': '<regex("[a-zA-Z0-9_-]*"):run_id>/vehicle',
        'schema': schema,
        'auto_add_user': True,
        'mongo_indexes': {
            # 'status_index': [('status', 1)],
            'state_index': [
                ('run_id', 1),
                ('state', 1)
            ],
            'unique_registration_index': (
                [
                    ('run_id', 1),
                    # ('user', 1),
                    ('registration.num', 1),
                    ('registration.country', 1),
                ],
                {'unique': True}
            ),
            'unique_driver_registration_index': (
                [
                    ('run_id', 1),
                    # ('user', 1),
                    ('authorised_drivers', 1),
                    ('registration.num', 1),
                    ('registration.country', 1),
                ],
                {'unique': True}
            ),
        },
        'resource_methods': ['GET', 'POST'],
        'item_methods': ['GET', 'PATCH', 'DELETE']
    }

