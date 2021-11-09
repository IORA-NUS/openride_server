from flask import current_app as app
from flask import abort, Response, jsonify
import json, logging

from api.state_machine import RidehailPassengerTripStateMachine
# from api.utils import Status
# from api.models import PassengerTripStates
from eve.methods.post import post_internal


class PassengerRideHailTripStateMachine_Managed(RidehailPassengerTripStateMachine):

    def on_end_trip(self, doc):
        doc['is_active'] = False

    def on_cancel(self, doc):
        doc['is_active'] = False


class PassengerRideHailTripController:
    ''' '''

    @classmethod
    def validate(cls, document, updates={}):
        ''' '''
        db = app.data.driver.db
        if updates != {}:
            # On Update
            # allow update only if trip is_active=True
            if document['is_active'] == False:
                # raise Exception('Cannot update when is_active is False')
                logging.info(f'Cannot update when is_active is False. PassengerRideHailTripController', document['_id'], updates)

            # Update state
            try:
                machine = PassengerRideHailTripStateMachine_Managed(start_value=document['state'])
                machine.run(updates.get('transition'), updates)
                updates['state'] = machine.current_state.identifier
                updates['feasible_transitions'] = [t.identifier for t in machine.current_state.transitions]
            except Exception as e:
                if updates.get('transition') is not None:
                    raise e

            # # Update trip.is_active = False if the trip is ending
            # # check to ensure Only one active trip is allowed
            # # This is important as New trip can be active only if No active trips exist.
            # if updates.get('state') in [machine.passenger_cancelled_trip.identifier,
            #                         machine.passenger_completed_trip.identifier]:
            #     # print('inside updating is_active')
            #     updates['is_active'] = False
        else:
            # On Insert, check to ensure Only one active trip is allowed
            passenger_ride_hail_trip = db['passenger_ride_hail_trip'].find_one({
                                                                        'run_id': document['run_id'],
                                                                        'user': document['user'],
                                                                        'passenger': document['passenger'],
                                                                        'is_active': True
                                                                    })

            if passenger_ride_hail_trip is None:
                document['is_active'] = True
            else:
                raise Exception(f"Passenger cannot have more than one active trip: {passenger_ride_hail_trip['_id']}")

    @classmethod
    def add_waypoint(cls, document, updates={}):
        db = app.data.driver.db
        waypoint = {
            'trip': document['_id'],
            'event': {
                'location': updates.get('current_loc', document['current_loc']),
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

        resp =  post_internal('waypoint', waypoint)
        # print(f"{resp[0]=}")
        if resp[0].get('_status') == 'ERR':
            raise Exception(resp[0])

        waypoint_id = resp[0]['_id']
        res = db['passenger_ride_hail_trip'].update({'_id': document['_id']},
                                        {
                                            "$inc": {
                                                'num_waypoints': 1
                                            },
                                        })

        # Update Trip stats from waypoint if is_active is updated from True to False
        if (updates.get('is_active') == False) and (document.get('is_active') == True):
            # waypoint = db['waypoint'].find_one({'trip': document['_id']}, sort=[('_created', -1)])
            waypoint = db['waypoint'].find_one({'_id': waypoint_id})
            # print(f"{waypoint=}")

            if waypoint is not None:
                res = db['passenger_ride_hail_trip'].update({'_id': document['_id']},
                                                        {
                                                            "$set": {
                                                                'stats': waypoint['cumulative_stats'],
                                                                'latest_waypoint': waypoint['_id']
                                                            },
                                                        })
