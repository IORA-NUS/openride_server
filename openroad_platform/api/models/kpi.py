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


class Kpi:

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
        # 'auto_add_user': True,
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









# class WaypointEvent(EmbeddedDocument):
#     location = PointField(required=True)
#     timestamp = DateTimeField(required=False) #, default=datetime.utcnow)
#     activity = EnumField(enum=Status, required=False) #, default=ActivityStatus.others)


# class WaypointStats(EmbeddedDocument):
#     distance = IntField(required=True, default=0) # in meters
#     time = IntField(required=True, default=0) # in seconds
#     speed = FloatField(required=True, default=0) # m/sec

