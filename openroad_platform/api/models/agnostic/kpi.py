from datetime import datetime
from api.utils import Status
from statemachine import State, StateMachine

# from api.state_machine import RidehailDriverTripStateMachine, RidehailPassengerTripStateMachine

class Kpi:
    """
    Kpi model definition for KPI (Key Performance Indicator) data.

    Attributes:
        schema (dict): Defines the structure and validation rules for KPI documents.
            - run_id (str): Unique identifier for the run. Required.
            - metric (str): Name of the metric. Required.
            - value (float): Value of the metric. Required, defaults to 0.
            - sim_clock (datetime, optional): Simulation clock timestamp.

        model (dict): Configuration for the KPI resource endpoint.
            - datasource (dict): Specifies the data source as 'kpi'.
            - url (str): URL pattern for accessing KPI resources by run_id.
            - schema (dict): Reference to the KPI schema.
            - mongo_indexes (dict): MongoDB index definitions, including a unique index on (run_id, metric, sim_clock).
            - resource_methods (list): Allowed HTTP methods for the resource.
            - item_methods (list): Allowed HTTP methods for individual items.

        metric (dict): Configuration for accessing individual KPI metrics.
            - datasource (dict): Specifies the data source as 'kpi'.
            - url (str): URL pattern for accessing a specific metric by run_id and metric name.
            - schema (dict): Reference to the KPI schema.
            - resource_methods (list): Allowed HTTP methods for the resource.
            - item_methods (list): Allowed HTTP methods for individual items.
    """

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

