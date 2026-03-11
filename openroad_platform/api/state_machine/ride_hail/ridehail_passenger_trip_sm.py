from statemachine import State, StateMachine

class RidehailPassengerTripStateMachine(StateMachine):
    """
    State machine for managing the lifecycle of a ride-hailing passenger trip.

    States:
        - passenger_requested_trip: Passenger has requested a trip (initial state).
        - passenger_assigned_trip: Trip has been assigned to a driver.
        - passenger_received_trip_confirmation: Passenger has received trip confirmation.
        - passenger_accepted_trip: Passenger has accepted the trip.
        - passenger_cancelled_trip: Trip has been cancelled by the passenger.
        - passenger_moving_for_pickup: Passenger is moving towards the pickup location.
        - passenger_waiting_for_pickup: Passenger is waiting to be picked up.
        - passenger_pickedup: Passenger has been picked up by the driver.
        - passenger_moving_for_dropoff: Passenger is en route to the dropoff location.
        - passenger_waiting_for_dropoff: Passenger is waiting to be dropped off.
        - passenger_droppedoff: Passenger has been dropped off.
        - passenger_completed_trip: Trip has been completed.

    Transitions:
        - assign: Assigns a driver to the requested trip.
        - driver_confirmed_trip: Driver confirms the assigned trip.
        - accept: Passenger accepts the confirmed trip.
        - reject: Passenger rejects the confirmed trip.
        - move_for_pickup: Passenger starts moving towards pickup.
        - wait_for_pickup: Passenger waits for pickup.
        - driver_cancelled_trip: Driver cancels the trip.
        - driver_arrived_for_pickup: Driver arrives for pickup.
        - driver_move_for_dropoff: Driver starts moving towards dropoff.
        - driver_arrived_for_dropoff: Driver arrives for dropoff.
        - driver_waiting_for_dropoff: Driver waits for dropoff.
        - end_trip: Trip ends after passenger is dropped off.
        - cancel: Passenger cancels the trip.
        - force_quit: Forcefully cancels the trip from any state.

    Class Methods:
        - is_moving(state): Returns True if the passenger is in a moving state, False otherwise.
        - is_driver_channel_open(state): Returns True if the driver communication channel should be open for the given state.

    Instance Methods:
        - on_end_trip(doc): Marks the trip as inactive when ended.
        - on_cancel(doc): Marks the trip as inactive when cancelled.

    Constants:
        - WAITING_STATES: Set of states where the passenger is waiting.
        - DRIVER_CHANNEL_OPEN_STATES: Set of states where the driver channel is open.
    """

    # passenger_online = State('passenger_online', initial=True)
    passenger_requested_trip = State('passenger_requested_trip', initial=True)
    passenger_assigned_trip = State('passenger_assigned_trip')
    passenger_received_trip_confirmation = State('passenger_received_trip_confirmation')
    passenger_accepted_trip = State('passenger_accepted_trip')
    passenger_cancelled_trip = State('passenger_cancelled_trip')
    passenger_moving_for_pickup = State('passenger_moving_for_pickup')
    passenger_waiting_for_pickup = State('passenger_waiting_for_pickup')
    passenger_pickedup = State('passenger_pickedup')
    passenger_moving_for_dropoff = State('passenger_moving_for_dropoff')
    passenger_waiting_for_dropoff = State('passenger_waiting_for_dropoff')
    passenger_droppedoff = State('passenger_droppedoff')
    passenger_completed_trip = State('passenger_completed_trip')


  # request_trip = passenger_online.to(passenger_requested_trip)
    assign = passenger_requested_trip.to(passenger_assigned_trip)
    driver_confirmed_trip = passenger_assigned_trip.to(passenger_received_trip_confirmation)
    # accept = passenger_assigned_trip.to(passenger_accepted_trip)
    accept = passenger_received_trip_confirmation.to(passenger_accepted_trip)
    # deny = passenger_requested_trip.to(passenger_completed_trip)
    reject = passenger_received_trip_confirmation.to(passenger_requested_trip)

    move_for_pickup = passenger_accepted_trip.to(passenger_moving_for_pickup)
    wait_for_pickup = passenger_accepted_trip.to(passenger_waiting_for_pickup) | passenger_moving_for_pickup.to(passenger_waiting_for_pickup)

    driver_cancelled_trip = passenger_requested_trip.from_(passenger_accepted_trip, passenger_moving_for_pickup, passenger_waiting_for_pickup)

    # pickedup = passenger_pickedup.from_(passenger_accepted_trip, passenger_moving_for_pickup, passenger_waiting_for_pickup)
    driver_arrived_for_pickup = passenger_pickedup.from_(passenger_accepted_trip, passenger_moving_for_pickup, passenger_waiting_for_pickup)
    # move_for_dropoff = passenger_pickedup.to(passenger_moving_for_dropoff)
    driver_move_for_dropoff = passenger_pickedup.to(passenger_moving_for_dropoff)
    driver_arrived_for_dropoff = passenger_moving_for_dropoff.to(passenger_waiting_for_dropoff)
    # droppedoff = passenger_moving_for_dropoff.to(passenger_droppedoff) | passenger_waiting_for_dropoff.to(passenger_droppedoff)
    driver_waiting_for_dropoff = passenger_moving_for_dropoff.to(passenger_droppedoff) | passenger_waiting_for_dropoff.to(passenger_droppedoff)
    end_trip = passenger_droppedoff.to(passenger_completed_trip)

    # cancel = passenger_cancelled_trip.from_(passenger_requested_trip, passenger_accepted_trip, passenger_moving_for_pickup, passenger_waiting_for_pickup)
    cancel = passenger_cancelled_trip.from_(passenger_requested_trip,
                                            passenger_assigned_trip,
                                            passenger_received_trip_confirmation,
                                            passenger_accepted_trip,
                                            passenger_moving_for_pickup,
                                            passenger_waiting_for_pickup)

    force_quit = passenger_cancelled_trip.from_(
                                passenger_requested_trip,
                                passenger_assigned_trip,
                                passenger_received_trip_confirmation,
                                passenger_accepted_trip,
                                passenger_moving_for_pickup,
                                passenger_waiting_for_pickup,
                                passenger_pickedup,
                                passenger_moving_for_dropoff,
                                passenger_waiting_for_dropoff,
                                passenger_droppedoff,
                            )

    WAITING_STATES = {
        passenger_requested_trip.identifier,
        passenger_assigned_trip.identifier,
        passenger_accepted_trip.identifier,
        passenger_cancelled_trip.identifier,
        passenger_waiting_for_dropoff.identifier,
        passenger_droppedoff.identifier,
        passenger_completed_trip,
    }

    DRIVER_CHANNEL_OPEN_STATES = {
        passenger_assigned_trip.identifier,
        passenger_accepted_trip.identifier,
        passenger_moving_for_pickup.identifier,
        passenger_waiting_for_pickup.identifier,
        passenger_pickedup.identifier,
        passenger_moving_for_dropoff.identifier,
        passenger_waiting_for_dropoff.identifier,
    }


    @classmethod
    def is_moving(cls, state):
        if state in cls.WAITING_STATES:
            return False
        else:
            return True


    @classmethod
    def is_driver_channel_open(cls, state):
        if state in cls.DRIVER_CHANNEL_OPEN_STATES:
            return True
        else:
            return False

    def on_end_trip(self, doc=None):
        if doc is not None:
            doc['is_active'] = False

    def on_cancel(self, doc=None):
        if doc is not None:
            doc['is_active'] = False

