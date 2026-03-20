from flask import abort, Response
import json

# from api.utils import Status
# from .waypoint import WaypointEventSchema
from api.utils import statemachine_schema, persona_schema

# from api.state_machine import WorkflowStateMachine

# from statemachine import State, StateMachine
# from .user import WorkflowStates

# class PassengerStates(StateMachine):
#     ''' '''

#     dormant = State('dormant', initial=True)
#     offline = State('offline')
#     online = State('online')

#     register = dormant.to(offline)
#     deregister = offline.to(dormant)
#     login = offline.to(online)
#     logout = offline.from_(online)




class Passenger:
    """
    Passenger model definition for the OpenRoad platform.

    Attributes:
        profile_schema (dict): Schema for passenger profile, including market and patience.
        schema (dict): Main schema for passenger data, including run_id, state, transition, is_busy, profile, and sim_clock.
        model (dict): Model configuration for data source, URL routing, schema, MongoDB indexes, and allowed resource/item methods.

    Schema Fields:
        - run_id (str): Unique identifier for the run. Required.
        - state (str): Current workflow state. Allowed values are dynamically generated from WorkflowStateMachine. Required and read-only.
        - transition (str): Workflow transition identifier. Allowed values are dynamically generated from WorkflowStateMachine. Optional.
        - is_busy (bool): Indicates if the passenger is busy. Optional.
        - profile (dict): Passenger profile, validated against profile_schema. Required.
        - sim_clock (datetime): Simulation clock timestamp. Optional.

    MongoDB Indexes:
        - run_id_index: Index on run_id.
        - state_index: Compound index on run_id, user, and state.
        - run_id_user_index: Unique compound index on run_id and user.

    Resource Methods:
        - GET, POST for collection-level operations.
        - GET, PATCH for item-level operations.
    """

    profile_schema = {
        'market': { # patience in Seconds
            'type': 'string',
            'required': True,
            'allowed': ['RideHail']
        },
        'patience': { # patience in Seconds
            'type': 'integer',
            'min': 0,
            'required': True,
            'default': 300
        }
    }


    schema = {
        'run_id': {
            'type': 'string',
            'required': True,
        },

        'state': {
            'type': 'string',
            # 'allowed': [s.name for s in WorkflowStateMachine().states],
            # 'default': WorkflowStateMachine().current_state.name,
            'required': True,
            # 'readonly': True
        },
        'transition': {
            'type': 'string',
            # 'allowed': [t.name for t in WorkflowStateMachine().events],
            'required': False,
        },

        'is_busy': {
            'type': 'boolean',
            # 'allowed': [True,],
            'required': False,
            # 'default': False,
            # 'nullable': True
        },

        'profile': {
            'type': 'dict',
            'schema': profile_schema,
            'required': True,
        },

        # Dynamic StateMachine fields
        'statemachine': {
            'type': 'dict',
            'schema': statemachine_schema,
            'required': True,
            # 'readonly': True,
        },

        'persona': {
            'type': 'dict',
            'schema': persona_schema,
            'required': True,
            # 'readonly': True,
        },

        'sim_clock': {
            'type': 'datetime',
            'required': False
        },
    }

    model = {
        'datasource': {
            'source': 'passenger',
        },
        'url': '<regex("[a-zA-Z0-9_-]*"):run_id>/passenger',
        'schema': schema,
        # 'auto_add_user': True,
        'mongo_indexes': {
            'run_id_index':[
                ('run_id', 1),
            ],
            'state_index': [
                ('run_id', 1),
                ('user', 1),
                ('state', 1)
            ],
            'run_id_user_index': (
                [
                    ('run_id', 1),
                    ('user', 1),
                ],
                {'unique': True}
            )
        },
        'resource_methods': ['GET', 'POST'],
        'item_methods': ['GET', 'PATCH']
    }

