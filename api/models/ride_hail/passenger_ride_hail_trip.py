from datetime import datetime
from api.utils import Status
from api.state_machine import RidehailPassengerTripStateMachine



class PassengerRideHailTrip:

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

    passenger_route_types_schema = {
                'moving_for_dropoff': {
                    'type': 'dict',
                    'required': False,
                },
            }

    routes_schema = {
        'planned': {
            'type': 'dict',
            'required': False,
            'schema': passenger_route_types_schema,
        },
        'actual': {
            'type': 'dict',
            'required': False,
            'schema': passenger_route_types_schema,
        },
    }

    schema = {
        'run_id': {
            'type': 'string',
            'required': True,
        },

        'passenger': {
            'type': 'objectid',
            'data_relation': {
                'resource': 'passenger',
                'field': '_id',
                'embeddable': True
            },
            'required': True,
        },
        'current_loc': {
            'type': 'point',
            'required': True,
        }, # Current_loc can be different from start loc to cater for passenger to walk to pickup location,

        'pickup_loc': {
            'type': 'point',
            'required': True,
        },
        'dropoff_loc': {
            'type': 'point',
            'required': True,
        },
        'trip_value': {
            'type': 'number',
            'required': True,
            'default': 0,
        },

        'is_active': {
            # Only one trip can exist with is_active=True
            'type': 'boolean',
        },

        'driver': {
            'type': 'objectid',
            # 'data_relation': {
            #     'resource': 'driver',
            #     'field': '_id'
            # },
            'required': False,
        },
        'driver_ride_hail_trip': {
            'type': 'objectid',
            # 'data_relation': {
            #     'resource': 'driver_ride_hail_trip',
            #     'field': '_id'
            # },
            'required': False,
        },

        'state': {
            'type': 'string',
            'allowed': [s.identifier for s in RidehailPassengerTripStateMachine().states],
            'default': RidehailPassengerTripStateMachine().current_state.identifier,
            'required': True,
            'readonly': True
        },
        'transition': {
            'type': 'string',
            'allowed': [t.identifier for t in RidehailPassengerTripStateMachine().transitions],
            'required': False,
        },
        'feasible_transitions': {
            'type': 'list',
            'allowed': [t.identifier for t in RidehailPassengerTripStateMachine().transitions],
            'default': [],
            'required': True,
            'readonly': True
        },

        'routes': {
            'type': 'dict',
            'required': False,
            'schema': routes_schema,
        },

        'latest_waypoint': {
            'type': 'objectid',
            'required': False,
        },
        'stats': {
            'type': 'dict',
            'schema': stats_schema,
            'required': False,
            'readonly': True
        },
        'num_waypoints': {
            'type': 'integer',
            # 'default': 0,
            'readonly': True
        },

        'force_quit': {
            'type': 'boolean',
            'required': False,
            'allowed': [True],
            'nullable': True,
        },

        'sim_clock': {
            'type': 'datetime',
            'required': False
        },

    }

    model = {
        'datasource': {
            'source': 'passenger_ride_hail_trip',
        },
        'url': '<regex("[a-zA-Z0-9_-]*"):run_id>/passenger/ride_hail/trip',
        'schema': schema,
        # 'auto_add_user': True,
        'mongo_indexes': {
            'passenger_trip_index':[
                ('run_id', 1),
                ('user', 1),
                ('passenger', 1),
                ('is_active', 1),
            ],

            'passenger_history_index': [
                ('run_id', 1),
                ('user', 1),
                ('passenger', 1),
                ('_created', -1),
            ],
            'pickup_loc_index': [
                ('run_id', 1),
                ('user', 1),
                ('state', 1),
                ('pickup_loc', '2dsphere'),
                ('is_active', 1),
                # ('_created', -1),
            ],
           'active_trips_index': [
                ('run_id', 1),
                ('user', 1),
                ('is_active', 1),
            ],
            'recenttrips_by_state_index': [
                ('run_id', 1),
                ('user', 1),
                ('state', 1),
                ('sim_clock', 1),
            ],
            'dropoff_loc_index': [
                ('run_id', 1),
                ('user', 1),
                ('state', 1),
                ('dropoff_loc', '2dsphere'),
                ('is_active', 1),
                # ('_created', -1),
            ],

            'force_quit_index': (
                [
                    ('run_id', 1),
                    ('user', 1),
                    ('force_quit', 1),
                ],
                {'sparse': 1}
            )
        },

        'resource_methods': ['GET', 'POST'],
        'item_methods': ['GET', 'PATCH'],
    }











# class WaypointEvent(EmbeddedDocument):
#     location = PointField(required=True)
#     timestamp = DateTimeField(required=False) #, default=datetime.utcnow)
#     activity = EnumField(enum=Status, required=False) #, default=ActivityStatus.others)


# class WaypointStats(EmbeddedDocument):
#     distance = IntField(required=True, default=0) # in meters
#     time = IntField(required=True, default=0) # in seconds
#     speed = FloatField(required=True, default=0) # m/sec

