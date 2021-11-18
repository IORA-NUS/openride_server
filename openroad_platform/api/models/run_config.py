from datetime import datetime
from api.utils import Status
from statemachine import State, StateMachine

from api.state_machine import RidehailDriverTripStateMachine, RidehailPassengerTripStateMachine


class RunConfig:

    schema = {
        'run_id': {
            'type': 'string',
            'required': True,
        },
        'name': {
            'type': 'string',
            'required': True,
        },
        'status': {
            'type': 'string',
            'required': False,
            'nullable': True,
        },
        'meta': {
            'type': 'dict',
            'required': True,
        },
        'execution_time': {
            'type': 'float',
            'required': False,
            'nullable': True,
        },
        'step_metrics': {
            'type': 'dict',
            'required': False,
            'nullable': True,
        },

    }

    model = {
        'datasource': {
            'source': 'run_config',
        },
        'url': 'run_config',
        'schema': schema,
        'mongo_indexes': {
            # 'latest_state_index': [
            #     ('run_id', 1),
            #     ('event.state', 1),
            #     ('_created', -1),
            # ],

            # 'trip_index': [
            #     ('run_id', 1),
            #     ('trip', 1),
            #     ('counter', 1),
            # ],
            'name_index': [
                ('name', 1),
            ],
            'unique_run_id_index': (
                [
                    ('run_id', 1),
                ],
                {'unique': True}
            ),
            'status_index': [
                ('status', 1),
                ('_updated', 1),
            ],

        },
        'resource_methods': ['GET', 'POST'], # , 'POST'
        'item_methods': ['GET', 'PATCH'],
    }

