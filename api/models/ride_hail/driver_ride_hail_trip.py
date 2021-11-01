from datetime import datetime
from api.utils import Status
from api.lib import RidehailDriverTripStateMachine


class DriverRideHailTrip:

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

    driver_route_types_schema = {
                'looking_for_job': {
                    'type': 'dict',
                    'required': False,
                },
                'moving_to_pickup': {
                    'type': 'dict',
                    'required': False,
                },
                'moving_to_dropoff': {
                    'type': 'dict',
                    'required': False,
                },
            }

    routes_schema = {
        'planned': {
            'type': 'dict',
            'required': False,
            'schema': driver_route_types_schema,
        },
        'actual': {
            'type': 'dict',
            'required': False,
            'schema': driver_route_types_schema,
        },
    }


    schema = {
        'run_id': {
            'type': 'string',
            'required': True,
        },
        'driver': {
            'type': 'objectid',
            'data_relation': {
                'resource': 'driver',
                'field': '_id',
                'embeddable': True
            },
            'required': True,
        },
        'vehicle': {
            'type': 'objectid',
            'data_relation': {
                'resource': 'vehicle',
                'field': '_id'
            },
            'required': True,
        },
        'current_loc': {
            'type': 'point',
            'required': True,
        },
        'next_dest_loc': {
            'type': 'point',
            'required': True,
        }, # next_est_loc should always be updated to reflect the current leg of the Driver trip

        'passenger': {
            'type': 'objectid',
            'data_relation': {
                'resource': 'passenger',
                'field': '_id'
            },
            'required': False,
        },

        'passenger_ride_hail_trip': {
            'type': 'objectid',
            # 'data_relation': {
            #     'resource': 'passenger_ride_hail_trip',
            #     'field': '_id'
            # },
            'required': False,
        },


        'state': {
            'type': 'string',
            'allowed': [s.identifier for s in RidehailDriverTripStateMachine().states],
            'default': RidehailDriverTripStateMachine().current_state.identifier,
            'required': True,
            'readonly': True
        },
        'transition': {
            'type': 'string',
            'allowed': [t.identifier for t in RidehailDriverTripStateMachine().transitions],
            'required': False,
        },
        'feasible_transitions': {
            'type': 'list',
            'allowed': [t.identifier for t in RidehailDriverTripStateMachine().transitions],
            'default': [],
            'required': True,
            'readonly': True
        },

        # Laden Trip Geolocations
        # NOTE might extend for multiple Pickup and dropoff
                # 'start_loc': {
                #     'type': 'point',
                #     'required': True,
                # },
                # 'end_loc': {
                #     'type': 'point',
                #     'required': False,
                # },
        'trip_start_loc': {
            'type': 'point',
            'required': False,
        }, # Set to current loc when Driver accepts trip
        'pickup_loc': {
            'type': 'point',
            'required': False,
        }, # From Passenger trip pickup_loc
        'dropoff_loc': {
            'type': 'point',
            'required': False,
        },# From Passenger trip dropoff_loc



        'is_occupied': {
            # False: No passenger. Driver is moving without any jod on hand.
            # True: Assigned passenger. Driver is in process of serving the passenger
            'type': 'boolean',
            'required': True,
            'default': False,
        },
        'is_active': {
            # Only one trip can exist with is_active=True
            'type': 'boolean',
            # 'readonly': True,
        },

        'routes': {
            'type': 'dict',
            'required': False,
            'schema': routes_schema,
        },
        'current_route_coords': {
            'type': 'list',
            'required': False,
            'nullable': True,
        },

        'force_quit': {
            'type': 'boolean',
            'required': False,
            'allowed': [True],
            'nullable': True,
        },
        # 'route_moving_to_pickup': {
        #     'type': 'dict',
        #     'required': False,
        # },
        # 'route_moving_to_dropoff': {
        #     'type': 'dict',
        #     'required': False,
        # },

        # 'route_off_service': {
        #     'type': 'dict',
        #     'required': False,
        # },


        # 'last_known': {
        #     'type': 'boolean',
        #     'required': True,
        # },
        # 'event': {
        #     'type': 'dict',
        #     'schema': event_schema,
        #     'required': False
        # },
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

        'sim_clock': {
            'type': 'datetime',
            'required': False
        },

    }

    model = {
        'datasource': {
            'source': 'driver_ride_hail_trip',
        },
        'url': '<regex("[a-zA-Z0-9_-]*"):run_id>/driver/ride_hail/trip',
        'schema': schema,
        'auto_add_user': True,
        'mongo_indexes': {
            'driver_trip_index':[
                ('run_id', 1),
                ('driver', 1),
                ('is_active', 1),
            ],
            'driver_history_index': [
                ('run_id', 1),
                ('driver', 1),
                # ('is_occupied', 1),
                ('_created', -1),
            ],
            'vehicle_history_index': [
                ('run_id', 1),
                ('vehicle', 1),
                ('driver', 1),
                # ('is_occupied', 1),
                ('_created', -1),
            ],
            'passenger_history_index': [
                ('run_id', 1),
                ('passenger', 1),
                ('driver', 1),
                ('_created', -1),
            ],
            'driver_trip_occupied_index':[
                ('run_id', 1),
                ('is_occupied', 1),
            ],
            'driver_assignment_index':[
                ('run_id', 1),
                ('is_occupied', 1),
                ('is_active', 1),
                ('current_loc', '2dsphere'),
            ],

            # 'driver_distance_index': [
            #     ('is_occupied', 1),
            #     ('driver', 1),
            #     ('stats.distance', -1),
            # ],
            # 'vehicle_distance_index': [
            #     ('is_occupied', 1),
            #     ('vehicle', 1),
            #     ('stats.distance', -1),
            # ],
            # 'passenger_distance_index': [
            #     ('passenger', 1),
            #     ('stats.distance', -1),
            # ],
            'current_loc_index': [
                ('run_id', 1),
                ('current_loc', '2dsphere'),
                ('is_active', 1),
                # ('_created', -1),
            ],
            'pickup_loc_index': [
                ('run_id', 1),
                ('pickup_loc', '2dsphere'),
                ('is_active', 1),
                # ('_created', -1),
            ],
            'dropoff_loc_index': [
                ('run_id', 1),
                ('dropoff_loc', '2dsphere'),
                ('is_active', 1),
                # ('_created', -1),
            ],
            'force_quit_trip_index': (
                [
                    ('run_id', 1),
                    ('force_quit', 1)
                    # ('_created', -1),
                ],
                {'sparse': True}
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

