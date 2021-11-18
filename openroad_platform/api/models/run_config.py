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
        'profile': {
            'type': 'dict',
            'required': True,
        },

    }

    model = {
        'datasource': {
            'source': 'run_config',
        },
        'url': '<regex("[a-zA-Z0-9_-]*"):run_id>/run_config',
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
            'unique_name_index': (
                [
                    ('name', 1),
                ],
                {'unique': True}
            ),
            'unique_run_id_index': (
                [
                    ('run_id', 1),
                ],
                {'unique': True}
            ),

        },
        'resource_methods': ['GET', 'POST'], # , 'POST'
        'item_methods': ['GET'],
    }

