
from statemachine import State, StateMachine

class RidehailDriverTripStateMachine(StateMachine):
    """
    RidehailDriverTripStateMachine manages the state transitions for a ride-hailing driver's trip lifecycle.

    States:
        - driver_init_trip: Initial state when the driver starts the trip process.
        - driver_looking_for_job: Driver is searching for a job.
        - driver_received_trip: Driver has received a trip offer.
        - driver_rejected_trip: Driver has rejected a trip offer.
        - driver_accepted_trip: Driver has accepted a trip offer.
        - driver_cancelled_trip: Trip has been cancelled by the driver.
        - driver_moving_to_pickup: Driver is en route to pick up the passenger.
        - driver_waiting_to_pickup: Driver is waiting at the pickup location.
        - driver_pickedup: Passenger has been picked up.
        - driver_moving_to_dropoff: Driver is en route to drop off the passenger.
        - driver_waiting_to_dropoff: Driver is waiting at the dropoff location.
        - driver_droppedoff: Passenger has been dropped off.
        - driver_completed_trip: Trip has been completed.

    Transitions:
        - look_for_job: From driver_init_trip to driver_looking_for_job.
        - recieve: From driver_init_trip to driver_received_trip.
        - confirm: From driver_received_trip to driver_accepted_trip.
        - passenger_confirmed_trip: From driver_accepted_trip to driver_moving_to_pickup.
        - wait_to_pickup: From driver_moving_to_pickup to driver_waiting_to_pickup.
        - passenger_cancelled_trip: From driver_accepted_trip, driver_moving_to_pickup, or driver_waiting_to_pickup to driver_completed_trip.
        - passenger_acknowledge_pickup: From driver_waiting_to_pickup to driver_pickedup.
        - move_to_dropoff: From driver_pickedup to driver_moving_to_dropoff.
        - wait_to_dropoff: From driver_moving_to_dropoff to driver_waiting_to_dropoff.
        - passenger_acknowledge_dropoff: From driver_waiting_to_dropoff to driver_droppedoff.
        - end_trip: From driver_droppedoff, driver_init_trip, driver_looking_for_job, or driver_rejected_trip to driver_completed_trip.
        - reject: From driver_received_trip to driver_rejected_trip.
        - cancel: From driver_accepted_trip, driver_moving_to_pickup, driver_waiting_to_pickup, or driver_looking_for_job to driver_cancelled_trip.
        - force_quit: From any state to driver_cancelled_trip.

    Class Attributes:
        - WAITING_STATES: Set of states where the driver is waiting (pickup/dropoff).
        - PASSENGER_CHANNEL_OPEN_STATES: Set of states where the passenger communication channel is open.

    Class Methods:
        - is_moving(state): Returns True if the driver is moving, False if waiting.
        - is_passenger_channel_open(state): Returns True if the passenger channel is open for the given state.

    Instance Methods:
        - on_end_trip(doc): Marks the trip as inactive when ending.
        - on_reject(doc): Marks the trip as inactive when rejected.
        - on_cancel(doc): Marks the trip as inactive when cancelled.
    """


    driver_init_trip = State('driver_init_trip', initial=True)
    driver_looking_for_job = State('driver_looking_for_job')
    driver_received_trip = State('driver_received_trip') # alternate Initial State
    driver_rejected_trip = State('driver_rejected_trip')
    driver_accepted_trip = State('driver_accepted_trip')
    driver_cancelled_trip = State('driver_cancelled_trip')
    driver_moving_to_pickup = State('driver_moving_to_pickup')
    driver_waiting_to_pickup = State('driver_waiting_to_pickup')
    driver_pickedup = State('driver_pickedup')
    driver_moving_to_dropoff = State('driver_moving_to_dropoff')
    driver_waiting_to_dropoff = State('driver_waiting_to_dropoff')
    driver_droppedoff = State('driver_droppedoff')
    driver_completed_trip = State('driver_completed_trip')


    look_for_job = driver_init_trip.to(driver_looking_for_job)
    recieve = driver_init_trip.to(driver_received_trip)
    confirm = driver_received_trip.to(driver_accepted_trip)
    passenger_confirmed_trip = driver_accepted_trip.to(driver_moving_to_pickup)

    wait_to_pickup = driver_moving_to_pickup.to(driver_waiting_to_pickup)

    passenger_cancelled_trip = driver_completed_trip.from_(driver_accepted_trip, driver_moving_to_pickup, driver_waiting_to_pickup)

    passenger_acknowledge_pickup = driver_pickedup.from_(driver_waiting_to_pickup)
    move_to_dropoff = driver_pickedup.to(driver_moving_to_dropoff)
    wait_to_dropoff = driver_moving_to_dropoff.to(driver_waiting_to_dropoff)

    # passenger_acknowledge_dropoff = driver_moving_to_dropoff.to(driver_droppedoff) | driver_waiting_to_dropoff.to(driver_droppedoff)
    passenger_acknowledge_dropoff = driver_waiting_to_dropoff.to(driver_droppedoff)
    end_trip = driver_completed_trip.from_(driver_droppedoff, driver_init_trip, driver_looking_for_job, driver_rejected_trip)

    reject = driver_rejected_trip.from_(driver_received_trip)
    cancel = driver_cancelled_trip.from_(driver_accepted_trip, driver_moving_to_pickup, driver_waiting_to_pickup, driver_looking_for_job)

    force_quit = driver_cancelled_trip.from_(
                            driver_init_trip,
                            driver_looking_for_job,
                            driver_received_trip,
                            driver_rejected_trip,
                            driver_accepted_trip,
                            driver_moving_to_pickup,
                            driver_waiting_to_pickup,
                            driver_pickedup,
                            driver_moving_to_dropoff,
                            driver_waiting_to_dropoff,
                            driver_droppedoff,
                        )

    WAITING_STATES = {
        driver_waiting_to_pickup.identifier,
        driver_waiting_to_dropoff.identifier,
    }

    PASSENGER_CHANNEL_OPEN_STATES = {
        driver_received_trip.identifier,
        driver_accepted_trip.identifier,
        driver_moving_to_pickup.identifier,
        driver_waiting_to_pickup.identifier,
        driver_pickedup.identifier,
        driver_moving_to_dropoff.identifier,
        driver_waiting_to_dropoff.identifier,
    }


    @classmethod
    def is_moving(cls, state):
        if state in cls.WAITING_STATES:
            return False
        else:
            return True

    @classmethod
    def is_passenger_channel_open(cls, state):
        if state in cls.PASSENGER_CHANNEL_OPEN_STATES:
            return True
        else:
            return False

    def on_end_trip(self, doc=None):
        if doc is not None:
            doc['is_active'] = False

    def on_reject(self, doc=None):
        if doc is not None:
            doc['is_active'] = False

    def on_cancel(self, doc=None):
        if doc is not None:
            doc['is_active'] = False
