from flask import abort, Response
import json

from api.utils import persona_schema

class Engine:
    """
    Engine model definition for the OpenRoad platform API.

    Attributes:
        schema (dict): Validation schema for Engine objects, specifying required fields and their types.
            - run_id (str): Unique identifier for the engine run. Required.
            - name (str): Name of the engine.
            - strategy (str): Strategy used by the engine.
            - planning_area (dict): Planning area details, including:
                - name (str): Name of the planning area. Required.
                - geometry: Geometry of the planning area. Required.
            - offline_params (dict): Parameters for offline operation.
            - online_params (dict): Parameters for online operation.
            - last_run_performance (dict): Performance metrics from the last run.
            - sim_clock (datetime, optional): Simulation clock timestamp.

        model (dict): Configuration for the Engine resource in the API.
            - datasource (dict): Source configuration for the engine.
            - url (str): URL pattern for accessing engine resources.
            - schema (dict): Reference to the validation schema.
            - allowed_roles (list): Roles allowed to access the resource.
            - mongo_indexes (dict): MongoDB index definitions for efficient querying.
            - resource_methods (list): Allowed HTTP methods on the resource.
            - item_methods (list): Allowed HTTP methods on individual items.
    """

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

        'persona': {
            'type': 'dict',
            'schema': persona_schema,
            'required': True,
            # 'readonly': True,
        },


    }

    model = {
        'datasource': {
            'source': 'ridehail_engine',
        },
        'url': '<regex("[a-zA-Z0-9_-]*"):run_id>/engine',
        'schema': schema,
        # 'auto_add_user': True,
        'allowed_roles': ['admin'],
        'mongo_indexes': {
            'run_id_index':[
                ('run_id', 1),
                ('sim_clock', 1),
            ],
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

