from datetime import datetime
from api.utils import Status
from statemachine import State, StateMachine

from api.state_machine import RidehailDriverTripStateMachine, RidehailPassengerTripStateMachine

class Kpi:

    schema = {
        'run_id': {
            'type': 'string',
            'required': True,
        },
        'metric': {
            'type': 'string',
            'required': True,
        },
        'value': {
            'type': 'float',
            'default': 0,
            'required': True,
        },

        'sim_clock': {
            'type': 'datetime',
            'required': False
        },
    }

    model = {
        'datasource': {
            'source': 'kpi',
        },
        'url': '<regex("[a-zA-Z0-9_-]*"):run_id>/kpi',
        'schema': schema,
        'mongo_indexes': {
            'unique_metric_index': (
                [
                    ('run_id', 1),
                    ('metric', 1),
                    ('sim_clock', 1),
                ],
                {'unique': True}
            ),

        },
        'resource_methods': ['GET', 'POST'], # , 'POST'
        'item_methods': ['GET'],
    }

    metric = {
        'datasource': {
            'source': 'kpi',
        },
        'url': '<regex("[a-zA-Z0-9_-]*"):run_id>/kpi/<regex("[a-zA-Z0-9_-]*"):metric>',
        'schema': schema,

        'resource_methods': ['GET', 'POST'],
        'item_methods': ['GET'],
    }

