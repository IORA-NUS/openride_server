from enum import Enum, unique, auto

class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name

@unique
class Status(AutoName):
    '''
    '''

    # user_created = auto()
    # user_activation_requested = auto()
    # user_activation_sent = auto()
    # user_activation_failed = auto()
    # user_active = auto()
    # # user_deleted = auto()


    # passenger_dormant = auto()
    # passenger_offline = auto()
    # passenger_online = auto()
    # passenger_moving_to_pickup = auto()
    # passenger_waiting_for_pickup = auto()
    # passenger_moving_to_dropoff = auto()
    # passenger_waiting_for_dropoff = auto()
    # passenger_trip_completed = auto()
    # passenger_cancelled = auto()

    # driver_dormant = auto()
    # driver_offline = auto()
    # driver_online = auto()
    # driver_available = auto()
    # driver_accepted_trip = auto()
    # driver_moving_to_pickup = auto()
    # driver_waiting_for_pickup = auto()
    # driver_moving_to_dropoff = auto()
    # driver_waiting_for_dropoff = auto()
    # driver_trip_completed = auto()

    # vehicle_dormant = auto()
    # vehicle_offline = auto()
    # vehicle_in_use = auto()

    trip_initialised = auto()
    trip_requested = auto()
    trip_waiting_for_assignment = auto()
    trip_accepted = auto()
    trip_moving_to_pickup = auto()
    trip_empty_move = auto()
    trip_waiting_for_pickup = auto()
    trip_empty_wait = auto()
    trip_pickup = auto()
    trip_moving_to_dropoff = auto()
    trip_occupied_move = auto()
    trip_occupied_wait = auto()
    trip_waiting_for_dropoff = auto()
    trip_dropoff = auto()
    trip_relocated = auto()
    trip_breakdown = auto()
    trip_completed = auto()
    trip_cancelled = auto()


# from enum import Enum

# class Status(Enum):
#     '''
#     Use a 4 digit code.
#     - Globals start with 1xxx
#     - Passenger starts with 2xxx
#     - Driver Starts wil 3xxx
#     - Vehicle Starts with 4xxx
#     - Trip Starts with 5xxx
#     '''

#     user_created = 1000
#     user_activation_requested = 1010
#     user_activation_sent = 1020
#     user_activation_failed = 1030
#     user_active = 1040
#     user_deleted = 1050


#     passenger_dormant = -2000
#     passenger_offline = 2000
#     passenger_online = 2010
#     passenger_moving_to_pickup = 2020
#     passenger_waiting_for_pickup = 2030
#     passenger_moving_to_dropoff = 2040
#     passenger_waiting_for_dropoff = 2050
#     passenger_trip_completed = 2060
#     passenger_cancelled = 2070

#     driver_dormant = -3000
#     driver_offline = 3000
#     driver_online = 3010
#     driver_available = 3020
#     driver_accepted_trip = 3030
#     driver_moving_to_pickup = 3040
#     driver_waiting_for_pickup = 3050
#     # busy = 5
#     driver_moving_to_dropoff = 3060
#     driver_waiting_for_dropoff = 3070
#     driver_trip_completed = 3080

#     vehicle_dormant = -4000
#     vehicle_offline = 4000
#     vehicle_in_use = 4010

#     # trip_initialised = -5000
#     trip_initialised = 5000
#     trip_requested = 5005
#     trip_waiting_for_assignment = 5010
#     trip_accepted = 5015
#     trip_moving_to_pickup = 5020
#     trip_empty_move = 5025
#     trip_waiting_for_pickup = 5030
#     trip_empty_wait = 5032
#     trip_pickup = 5035
#     trip_moving_to_dropoff = 5040
#     trip_occupied_move = 5045
#     trip_occupied_wait = 5047
#     trip_waiting_for_dropoff = 5050
#     trip_dropoff = 5055
#     trip_relocated = 5060
#     trip_breakdown = 5070
#     trip_completed = 5090
#     trip_cancelled = 5100
