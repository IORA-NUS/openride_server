from flask import abort, Response
import json


class Engine:

    schema = {
        'run_id': {
            'type': 'string',
            'required': True,
        },
        'name': {
            'type': 'string',
        },
        'strategy': {
            'type': 'string',
        },

        # 'area': {
        #     'type': 'multipolygon',
        #     'required': False
        # },
        'planning_area': {
            'type': 'dict',
            'schema': {
                'name': {
                    'type': 'string',
                    'required': True
                },
                'geometry': {
                    # 'type': 'multipolygon',
                    'required': True
                },
            },
            'required': True
        },

        'offline_params': {
            'type': 'dict',
        },

        'online_params': {
            'type': 'dict',
        },

        'last_run_performance': {
            'type': 'dict',
        },

        'sim_clock': {
            'type': 'datetime',
            'required': False
        },

    }

    model = {
        'datasource': {
            'source': 'engine',
        },
        'url': '<regex("[a-zA-Z0-9_-]*"):run_id>/engine',
        'schema': schema,
        'allowed_roles': ['admin'],
        'mongo_indexes': {
            'unique_name_index': (
                [
                    ('run_id', 1),
                    ('name', 1),
                ],
                {'unique': True}
            ),
        },
        'resource_methods': ['GET', 'POST'],
        'item_methods': ['GET', 'PATCH']
    }

