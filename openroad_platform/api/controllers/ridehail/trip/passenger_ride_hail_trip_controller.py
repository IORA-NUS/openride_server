import traceback
from flask import current_app as app
from flask import abort, Response, jsonify
import json, logging

# from api.state_machine import RidehailPassengerTripStateMachine
# from api.utils import Status
# from api.models import PassengerTripStates
from eve.methods.post import post_internal


# class PassengerRideHailTripStateMachine_Managed(RidehailPassengerTripStateMachine):

#     def on_end_trip(self, doc):
#         doc['is_active'] = False

#     def on_cancel(self, doc):
#         doc['is_active'] = False


class PassengerRideHailTripController:
    """
    Controller class for managing passenger ride-hail trips.

    This class provides methods for validating trip documents and handling updates,
    ensuring business rules such as only one active trip per passenger, and managing
    state transitions using a state machine. It also supports adding waypoints to trips,
    updating trip statistics, and maintaining trip activity status.

    Methods
    -------
    validate(document, updates={})
        Validates a trip document on insert or update. On update, ensures that only
        active trips can be updated and manages state transitions. On insert, checks
        that a passenger does not have more than one active trip.

    add_waypoint(document, updates={})
        Adds a waypoint to the trip, updates the trip's last waypoint and waypoint count,
        and optionally updates trip statistics if the trip becomes inactive.
    """

    @classmethod
    def validate(cls, document, updates={}):
        """
        Validates and manages state transitions for passenger ride hail trip documents.

        On update:
            - Allows updates only if the trip is currently active (`is_active=True`).
            - Handles state transitions using the RidehailPassengerTripStateMachine.
            - Updates the document's state and feasible transitions based on the state machine.
            - Logs an info message if an update is attempted on an inactive trip.
            - Raises an exception if an invalid state transition is requested.

        On insert:
            - Ensures that a passenger cannot have more than one active trip at a time.
            - Sets `is_active=True` if no other active trip exists for the passenger.
            - Raises an exception if an active trip already exists for the passenger.

        Args:
            document (dict): The trip document to validate.
            updates (dict, optional): The updates to apply to the document. Defaults to {}.

        Raises:
            Exception: If validation fails or an invalid state transition is attempted.
        """
        db = app.data.driver.db
        if updates != {}:
            # On Update
            # allow update only if trip is_active=True
            if not document['is_active']:
                # raise Exception('Cannot update when is_active is False')
                logging.info(f'Cannot update when is_active is False. PassengerRideHailTripController: document_id={document["_id"]}, updates={updates}')

            # Update state
            try:
                from api.utils.state_machine_cache import get_state_machine, get_definition_func
                statemachine_id = (
                    (updates.get('statemachine') or {}).get('id')
                    or (document.get('statemachine') or {}).get('id')
                )
                StateMachineClass = get_state_machine(statemachine_id, get_definition_func)
                machine = StateMachineClass(start_value=document['state'])
                transition = updates.get('transition')
                if transition is not None:
                    if not isinstance(transition, str):
                        raise Exception(f"Transition attribute must be a string, got {type(transition)}: {transition}")
                    getattr(machine, transition)()

                updates['state'] = machine.current_state.name
                updates['feasible_transitions'] = [t.name for t in machine.allowed_events]
                # Final state check
                if getattr(machine.current_state, 'final', False):
                    updates['is_active'] = False

            except Exception as e:
                logging.exception(f"Error during state transition '{updates.get('transition')}' with updates {updates}: {e}")
                if updates.get('transition') is not None:
                    raise Exception(f"Error during state transition '{updates.get('transition')}' with updates {updates}: {e}")

            # # Update trip.is_active = False if the trip is ending
            # # check to ensure Only one active trip is allowed
            # # This is important as New trip can be active only if No active trips exist.
            # if updates.get('state') in [machine.passenger_cancelled_trip.name,
            #                         machine.passenger_completed_trip.name]:
            #     # print('inside updating is_active')
            #     updates['is_active'] = False
        else:
            # On Insert, check to ensure Only one active trip is allowed
            ridehail_passenger_trip = db['ridehail_passenger_trip'].find_one({
                                                                        'run_id': document['run_id'],
                                                                        'user': document['user'],
                                                                        'passenger': document['passenger'],
                                                                        'is_active': True
                                                                    })

            if ridehail_passenger_trip is None:
                document['is_active'] = True
            else:
                raise Exception(f"Passenger cannot have more than one active trip: {ridehail_passenger_trip['_id']}")

    @classmethod
    def add_waypoint(cls, document, updates={}):
        """
        Adds a waypoint to a passenger ride hail trip and updates the trip document with the new waypoint.

        Args:
            document (dict): The trip document to which the waypoint will be added.
            updates (dict, optional): A dictionary of updates to apply to the waypoint. Defaults to {}.

        Raises:
            Exception: If there is an error while adding the waypoint or updating the trip document.

        Returns:
            None
        """
        db = app.data.driver.db
        waypoint = {
            'trip': document['_id'],
            'event': {
                'location': updates.get('current_loc', document['current_loc']),
                'traversed_path': updates.get('traversed_path', None),
                'state': updates.get('state', document['state']),
            },
            'agent': {
                'type': 'passenger',
                'id': document['passenger']
            }
        }

        if updates.get('sim_clock') is not None:
            waypoint['sim_clock'] = updates['sim_clock']
        elif document.get('sim_clock') is not None:
            waypoint['sim_clock'] = document['sim_clock']

        try:
            resp =  post_internal('waypoint', waypoint)
        except Exception as e:
            logging.exception("An error occurred while adding a waypoint: %s", traceback.format_exc())
            raise e

        # Handle tuple, list, and dict responses
        actual_resp = resp
        if isinstance(resp, tuple):
            actual_resp = resp[0]

        status_obj = None
        if isinstance(actual_resp, list) and len(actual_resp) > 0:
            status_obj = actual_resp[0]
        elif isinstance(actual_resp, dict):
            status_obj = actual_resp
        else:
            raise Exception(f"Unexpected response structure in add_waypoint: {actual_resp}")

        if not status_obj or status_obj.get('_status') == 'ERR':
            raise Exception(status_obj)

        waypoint_id = resp[0]['_id']

        # res = db['ridehail_passenger_trip'].update({'_id': document['_id']},
        #                                 {
        #                                     "$inc": {
        #                                         'num_waypoints': 1
        #                                     },
        #                                 })

        # # Update Trip stats from waypoint if is_active is updated from True to False
        # if (updates.get('is_active') == False) and (document.get('is_active') == True):
        #     # waypoint = db['waypoint'].find_one({'trip': document['_id']}, sort=[('_created', -1)])
        #     waypoint = db['waypoint'].find_one({'_id': waypoint_id})
        #     # print(f"{waypoint=}")

        #     if waypoint is not None:
        #         res = db['ridehail_passenger_trip'].update({'_id': document['_id']},
        #                                                 {
        #                                                     "$set": {
        #                                                         'stats': waypoint['cumulative_stats'],
        #                                                         'latest_waypoint': waypoint['_id']
        #                                                     },
        #                                                 })

        waypoint = db['waypoint'].find_one({'_id': waypoint_id})

        if waypoint is not None:
            res = db['ridehail_passenger_trip'].update_one({'_id': document['_id']},
                {
                    "$set": {
                        'last_waypoint': waypoint
                    },
                    "$inc": {
                        'num_waypoints': 1
                    },
                })

            if res.matched_count == 0:
                logging.error(f"Failed to update trip with ID {document['_id']}: No matching document found.")
                raise Exception(f"Failed to update trip with ID {document['_id']}: No matching document found.")
            elif res.modified_count == 0:
                logging.warning(f"No changes were made to the trip with ID {document['_id']}.")
