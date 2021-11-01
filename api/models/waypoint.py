from datetime import datetime
from api.utils import Status
from statemachine import State, StateMachine

from api.state_machine import RidehailDriverTripStateMachine, RidehailPassengerTripStateMachine

# from trip import TripStates
# from .driver_trip import DriverTripStates
# from .passenger_trip import PassengerTripStates

# class WaypointCounter:
#     schema = {
#         'record_num': {
#             'type': 'integer',
#             'required': True,
#         }
#     }

#     model = {
#         'datasource': {
#             'source': 'waypoint_counter',
#         },
#         # 'url': 'waypoint_counter',
#         'schema': schema,
#         'mongo_indexes': {
#             'counter_index': [
#                 ('record_num', 1),
#             ],
#         }
#     }


class Waypoint:

    event_schema = {
        'location': {
            'type': 'point',
            'required': True,
        },
        'state': {
            'type': 'string',
            'allowed': [s.identifier for s in RidehailDriverTripStateMachine().states] + [s.identifier for s in RidehailPassengerTripStateMachine().states],
            # 'default': DriverStates().current_state.identifier,
            'required': True,
            # 'readonly': True
        },
        # 'transition': {
        #     'type': 'string',
        #     'allowed': [t.identifier for t in DriverStates().transitions] + [s.identifier for s in PassengerStates().transitions],
        #     'required': False,
        #     'readonly': True,
        # },
    }

    agent_schema = {
        'type': {
            'type': 'string',
            'allowed': ['driver', 'passenger'],
            'required': True,
        },
        'id': {
            'type': 'objectid',
            'required': True,
        }

    }

    stats_schema = {
        'distance': {
            'type': 'float',
            'required': True,
            'default': 0
        },
        'duration': {
            'type': 'float',
            'required': True,
            'default': 0
        },
        'speed':{
            'type': 'float',
            # 'min_value': 0,
            'required': True,
            'default': 0
        }
    }

    schema = {
        'run_id': {
            'type': 'string',
            'required': True,
        },
        'trip': {
            'type': 'objectid',
        #     'data_relation': {
        #         'resource': 'trip',
        #         'field': '_id'
        #     },
            'required': True,
        },
        'counter': {
            'type': 'integer',
            'readonly': True,
        },
        'event': {
            'type': 'dict',
            'schema': event_schema,
            'required': False
        },
        'current_stats': {
            'type': 'dict',
            'schema': stats_schema,
            'required': False,
            'readonly': True
        },
        'cumulative_stats': {
            'type': 'dict',
            'schema': stats_schema,
            'required': False,
            'readonly': True
        },

        # 'entity': {
        #     'type': 'string',
        #     'allowed': ['driver', 'passenger'],
        #     'required': True
        # },

        'agent': {
            'type': 'dict',
            'schema': agent_schema,
            # 'allowed': ['driver', 'passenger'],
            'required': True
        },
        'sim_clock': {
            'type': 'datetime',
            'required': False
        },


    }

    model = {
        'datasource': {
            'source': 'waypoint',
        },
        'url': '<regex("[a-zA-Z0-9_-]*"):run_id>/waypoint',
        'schema': schema,
        'auto_add_user': True,
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
            'unique_counter_index': (
                [
                    ('run_id', 1),
                    ('trip', 1),
                    ('counter', 1),
                ],
                {'unique': True}
            ),
            'updated_trip_index': (
                [
                    ('run_id', 1),
                    ('trip', 1),
                    ('_updated', 1),
                ]
            ),
            'updated_agent_type_index': (
                [
                    ('run_id', 1),
                    # ('entity', 1),
                    ('agent.type', 1),
                    ('_updated', 1),
                ]
            ),
            'updated_agent_id_index': (
                [
                    ('run_id', 1),
                    # ('agent.type', 1),
                    ('agent.id', 1),
                    ('_updated', 1),
                ]
            ),
            'updated_alltrips_index': (
                [
                    ('run_id', 1),
                    ('_updated', 1),
                ]
            ),
        },
        # 'resource_methods': ['GET', 'POST'],
        'resource_methods': ['GET'], # , 'POST'
        'item_methods': ['GET'],
    }

    trip_waypoints = {
        'datasource': {
            'source': 'waypoint',
        },
        'url': '<regex("[a-zA-Z0-9_-]*"):run_id>/trip/<regex("[a-f0-9]{24}"):trip>/waypoint',
        'schema': schema,
        'auto_add_user': True,
        # 'mongo_indexes': {
        # #     'latest_state_index': [
        # #         ('event.state', 1),
        # #         ('_created', -1),
        # #     ],

        #     'unique_counter_index': (
        #         [
        #             ('run_id', 1),
        #             ('trip', 1),
        #             ('counter', 1),
        #         ],
        #         {'unique': True}
        #     )
        # },
        # 'resource_methods': ['GET', 'POST'],
        'resource_methods': ['GET'],
        'item_methods': ['GET'],
    }









# class WaypointEvent(EmbeddedDocument):
#     location = PointField(required=True)
#     timestamp = DateTimeField(required=False) #, default=datetime.utcnow)
#     activity = EnumField(enum=Status, required=False) #, default=ActivityStatus.others)


# class WaypointStats(EmbeddedDocument):
#     distance = IntField(required=True, default=0) # in meters
#     time = IntField(required=True, default=0) # in seconds
#     speed = FloatField(required=True, default=0) # m/sec

