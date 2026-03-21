from datetime import datetime
from api.utils import Status
from statemachine import State, StateMachine

# from api.state_machine import RidehailDriverTripStateMachine, RidehailPassengerTripStateMachine


class RunConfig:
    """
    RunConfig defines the schema and model configuration for a run configuration resource.

    Attributes:
        schema (dict): Specifies the validation rules for each field in the run configuration, including types, required status, and nullability.
            - run_id (str): Unique identifier for the run. Required.
            - name (str): Name of the run. Required.
            - status (str, optional): Status of the run. Nullable.
            - meta (dict): Metadata associated with the run. Required.
            - execution_time (float, optional): Execution time of the run. Nullable.
            - step_metrics (dict, optional): Metrics for each step in the run. Nullable.

        model (dict): Contains resource configuration for the run configuration, including:
            - datasource (dict): Source information for the resource.
            - url (str): Resource endpoint.
            - schema (dict): Reference to the schema definition.
            - mongo_indexes (dict): MongoDB index definitions for efficient querying and uniqueness constraints.
            - resource_methods (list): Allowed HTTP methods for the resource.
            - item_methods (list): Allowed HTTP methods for individual items.
    """

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
        'url': 'run-config',
        'schema': schema,
        'mongo_indexes': {
            'run_id_index': (
                [
                    ('run_id', 1),
                ],
                {'unique': True}
            ),
            'name_index': [
                ('name', 1),
                ('_updated', 1),
            ],
            'status_index': [
                ('status', 1),
                ('_updated', 1),
            ],
            'recent_index': [
                ('_updated', 1),
            ],

        },
        'resource_methods': ['GET', 'POST'], # , 'POST'
        'item_methods': ['GET', 'PATCH'],
    }

