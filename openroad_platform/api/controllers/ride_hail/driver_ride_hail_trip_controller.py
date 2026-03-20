from flask import current_app as app
from flask import abort, Response, jsonify
import json, logging
import traceback

# from api.utils import Status
# from api.models import DriverTripStates
from eve.methods.post import post, post_internal
# from api.state_machine import RidehailDriverTripStateMachine

# class DriverRideHailTripStateMachine_Managed(RidehailDriverTripStateMachine):

#     # def on_end_trip(self, doc):
#     def on_end_trip(self, doc):
#         doc['is_active'] = False

#     def on_reject(self, doc):
#         doc['is_active'] = False

#     def on_cancel(self, doc):
#         doc['is_active'] = False



class DriverRideHailTripController:
    """
    Controller for managing driver ride hail trip operations, including validation and waypoint management.

    This class provides methods to:
    - Validate trip documents during insert and update operations, enforcing business rules such as single active trip per driver and valid state transitions.
    - Add waypoints to trips, updating trip statistics and maintaining trip state consistency.

    Methods
    -------
    validate(document: dict, updates: dict = {}) -> None
        Validates and updates trip documents during insert and update operations, ensuring only one active trip per driver and handling state transitions.

    add_waypoint(document: dict, updates: dict = {}) -> None
        Adds a waypoint to a trip, posts the waypoint to the internal endpoint, and updates the trip document with the new waypoint and incremented waypoint count.

    Raises
    ------
    Exception
        If validation fails, state transitions are invalid, or database updates are unsuccessful.
    """

    @classmethod
    def validate(cls, document, updates={}):
        """
        Performs additional validation and auto-adds fields during pre-insert and pre-update hooks for driver ride hail trips.

        On update:
            - Allows updates only if the trip is active (`is_active=True`).
            - Handles state transitions using the RidehailDriverTripStateMachine.
            - Updates the trip's state and feasible transitions.
            - Logs and raises exceptions for invalid state transitions or updates when inactive.

        On insert:
            - Ensures that only one active trip exists per driver, run, and user.
            - Sets `is_active=True` if no active trip exists, otherwise raises an exception.

        Args:
            document (dict): The trip document to validate.
            updates (dict, optional): Fields to update in the document. Defaults to {}.

        Raises:
            Exception: If an invalid update or state transition is attempted, or if more than one active trip is detected for a driver.
        """

        db = app.data.driver.db
        if updates != {}:
            # On Update
            # allow update only if trip is_active=True
            if not document['is_active']:
                # raise Exception('Cannot update when is_active is False')
                logging.info(f'Cannot update when is_active is False. DriverRideHailTripController: document_id={document["_id"]}, updates={updates}')

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

        else:
            # On Insert, check to ensure Only one active trip is allowed
            driver_ride_hail_trip = db['driver_ride_hail_trip'].find_one({
                                                                    'run_id': document['run_id'],
                                                                    'user': document['user'],
                                                                    'driver': document['driver'],
                                                                    'is_active': True
                                                                })

            if driver_ride_hail_trip is None:
                document['is_active'] = True
            else:
                raise Exception(f"Driver cannot have more than one active trip: {driver_ride_hail_trip['_id']}")


    @classmethod
    def add_waypoint(cls, document, updates={}):
        """
        Adds a waypoint to a driver's ride hail trip and updates the trip document accordingly.

        This method creates a waypoint document based on the provided trip document and optional updates,
        posts it to the internal 'waypoint' endpoint, and updates the corresponding trip document in the
        database with the new waypoint and incremented waypoint count.

        Args:
            document (dict): The trip document containing trip and driver information.
            updates (dict, optional): A dictionary of updates to apply to the waypoint. Defaults to {}.

        Raises:
            Exception: If posting the waypoint fails or updating the trip document fails.

        Returns:
            None
        """
        db = app.data.driver.db
        # print("inside add_waypoint")
        # print(updates)
        waypoint = {
            # 'trip': str(document['_id']),
            'trip': document['_id'],
            'event': {
                'location': updates.get('current_loc', document['current_loc']),
                'traversed_path': updates.get('traversed_path', None),
                'state': updates.get('state', document['state']),
            },
            'agent': {
                'type': 'driver',
                'id': document['driver']
            }
        }

        if updates.get('sim_clock') is not None:
            waypoint['sim_clock'] = updates['sim_clock']
        elif document.get('sim_clock') is not None:
            waypoint['sim_clock'] = document['sim_clock']
        # print(waypoint)

        try:
            resp =  post_internal('waypoint', waypoint)
            # print(f"Waypoint post response: {resp}")
            # print(f"Waypoint post response: {resp[0]}")
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

        # res = db['driver_ride_hail_trip'].update({'_id': document['_id']},
        #                                 {
        #                                     "$inc": {
        #                                         'num_waypoints': 1
        #                                     },
        #                                 })

        # # Update Trip stats from waypoint if is_active is updated from True to False
        # if (updates.get('is_active') == False) and (document.get('is_active') == True):
        #     # # waypoint = db['waypoint'].find_one({'trip': document['_id']}, sort=[('_created', -1)])
        #     waypoint = db['waypoint'].find_one({'_id': waypoint_id})
        #     # print(f"{waypoint=}")

        #     if waypoint is not None:
        #         res = db['driver_ride_hail_trip'].update({'_id': document['_id']},
        #                                         {
        #                                             "$set": {
        #                                                 'stats': waypoint['cumulative_stats'],
        #                                                 'latest_waypoint': waypoint['_id']
        #                                             },
        #                                         })

        #         # print(res)

        waypoint = db['waypoint'].find_one({'_id': waypoint_id})

        if waypoint is not None:
            res = db['driver_ride_hail_trip'].update_one({'_id': document['_id']},
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

