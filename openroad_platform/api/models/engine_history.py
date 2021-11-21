from flask import abort, Response
import json


class EngineHistory:

    schema = {
        'run_id': {
            'type': 'string',
            'required': True,
        },
        'engine': {
            'type': 'objectid',
            'data_relation': {
                'resource': 'engine',
                'field': '_id'
            },
            'required': True,
        },

        'online_params': {
            'type': 'dict',
        },

        'runtime_performance': {
            'type': 'dict',
        },

        'sim_clock': {
            'type': 'datetime',
            'required': False
        },

    }

    model = {
        'datasource': {
            'source': 'engine_history',
        },
        'url': '<regex("[a-zA-Z0-9_-]*"):run_id>/engine/<regex("[a-f0-9]{24}"):engine>/history',
        'schema': schema,
        # 'auto_add_user': True,
        'allowed_roles': ['admin'],
        'mongo_indexes': {
            'run_id_index':[
                ('run_id', 1),
                ('sim_clock', 1),
            ],
            'history_index':[
                ('run_id', 1),
                ('engine', 1),
                ('sim_clock', -1)
            ],
        },
        'resource_methods': ['GET', 'POST'],
        'item_methods': ['GET']
    }

