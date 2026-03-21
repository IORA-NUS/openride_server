from flask import abort, Response
import json


class EngineHistory:
    """
    EngineHistory model defines the schema and configuration for storing and accessing engine history records.

    Attributes:
        schema (dict): Defines the structure of engine history documents, including:
            - run_id (str): Unique identifier for the engine run. Required.
            - engine (ObjectId): Reference to the engine resource (_id). Required.
            - online_params (dict): Parameters used during online operation.
            - runtime_performance (dict): Performance metrics collected during runtime.
            - sim_clock (datetime, optional): Simulation clock timestamp.

        model (dict): Configuration for the data source and API resource, including:
            - datasource (dict): Specifies the MongoDB collection ('engine_history').
            - url (str): URL pattern for accessing engine history by run_id and engine.
            - schema (dict): Reference to the schema definition.
            - allowed_roles (list): Roles permitted to access this resource (e.g., 'admin').
            - mongo_indexes (dict): MongoDB indexes for efficient querying.
            - resource_methods (list): Allowed HTTP methods on the resource (e.g., 'GET', 'POST').
            - item_methods (list): Allowed HTTP methods on individual items (e.g., 'GET').
    """

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
            # 'history_index':[
            #     ('run_id', 1),
            #     ('engine', 1),
            #     ('sim_clock', -1)
            # ],
        },
        'resource_methods': ['GET', 'POST'],
        'item_methods': ['GET']
    }

