from flask import abort, Response
import json

# from api.utils import Status
# from .waypoint import WaypointEventSchema

from api.state_machine import WorkflowStateMachine
# from statemachine import State, StateMachine
# from .user import WorkflowStates

# class DriverStates(StateMachine):
#     ''' '''
#     dormant = State('dormant', initial=True)
#     offline = State('offline')
#     online = State('online')

#     register = dormant.to(offline)
#     deregister = offline.to(dormant)
#     login = offline.to(online)
#     logout = online.to(offline)



class Driver:

    settings_schema = {
        'market': { # patience in Seconds
            'type': 'string',
            'required': True,
            'allowed': ['RideHail', 'PointToPointDelivery', 'HyperLocalDelivery']
        },
        'patience': { # patience in Seconds
            'type': 'integer',
            'min': 0,
            'required': True,
            'default': 300
        },
        'service_score': {
            'type': 'integer',
            'min': 0,
            'required': True,
            'default': 300
        }
    }

    license_schema = {
        'num': {
            'type': 'string',
            'minlength': 1,
            'maxlength': 32,
            'required': True,
            'unique_combination': ['num', 'country'],
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
        },
    }

    schema = {
        'run_id': {
            'type': 'string',
            'required': True,
        },

        # 'license_num': {
        #     'type': 'string',
        #     'minlength': 1,
        #     'maxlength': 32,
        #     'required': True,
        #     'unique_combination': ['license_num', 'license_country'],
        # },
        # 'license_country': {
        #     'type': 'string',
        #     'minlength': 1,
        #     'maxlength': 64,
        #     'required': True,
        # },
        # 'license_expiry': {
        #     'type': 'datetime',
        #     'required': True,
        # },

        'license': {
            'schema': license_schema,
            'type': 'dict',
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

        'settings': {
            'type': 'dict',
            'schema': settings_schema,
            'required': True,
            'default': {
                'patience': 300,
                'service_score': 0
            }
        },


        'is_busy': {
            'type': 'boolean',
            # 'allowed': [True,],
            'required': False,
            # 'default': False,
            # 'nullable': True
        },
        # 'waypoint': {
        #     'type': 'dict',
        #     'schema': WaypointEventSchema,
        #     'required': False
        # },

        # 'vehicle_list':{
        #     'type': 'list',
        #     # 'unique_in_list': ['id'],
        #     'schema': {
        #         'type': 'objectid',
        #         'data_relation': {
        #             'resource': 'vehicle',
        #             'field': '_id'
        #         },
        #     },
        # },

        # 'active_vehicle': {
        #     'type': 'objectid',
        #     'data_relation': {
        #         'resource': 'vehicle',
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
            'source': 'driver',
        },
        'url': '<regex("[a-zA-Z0-9_-]*"):run_id>/driver',
        'schema': schema,
        'auto_add_user': True,
        'mongo_indexes': {
            # 'status_index': [('status', 1)],
            'state_index': [
                ('run_id', 1),
                ('state', 1)
            ],
            'unique_user_index': (
                [
                    ('run_id', 1),
                    ('user', 1),
                    # ('license.country', 1),
                ],
                {'unique': True}
            ),
            'unique_license_index': (
                [
                    ('run_id', 1),
                    ('license.num', 1),
                    ('license.country', 1),
                ],
                {'unique': True},
            ),
        },
        'resource_methods': ['GET', 'POST'],
        'item_methods': ['GET', 'PATCH']
    }

