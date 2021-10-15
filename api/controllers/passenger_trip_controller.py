from flask import current_app as app
from flask import abort, Response, jsonify
import json

from api.lib import RidehailPassengerTripStateMachine
# from api.utils import Status
# from api.models import PassengerTripStates
from eve.methods.post import post_internal


class PassengerTripStateMachine_Managed(RidehailPassengerTripStateMachine):

    def on_end_trip(self, doc):
        doc['is_active'] = False

    def on_cancel(self, doc):
        doc['is_active'] = False


class PassengerTripController:
    ''' '''

    @classmethod
    def validate(cls, document, updates={}):
        ''' '''
        db = app.data.driver.db
        if updates != {}:
            # On Update
            # allow update only if trip is_active=True
            if document['is_active'] == False:
                raise Exception('Cannot update when is_active is False')

            # Update state
            try:
                machine = PassengerTripStateMachine_Managed(start_value=document['state'])
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
            passenger_trip = db['passenger_trip'].find_one({'passenger': document['passenger'], 'is_active': True})

            if passenger_trip is None:
                document['is_active'] = True
            else:
                raise Exception(f"Passenger cannot have more than one active trip: {passenger_trip['_id']}")

    @classmethod
    def add_waypoint(cls, document, updates={}):
        db = app.data.driver.db
        waypoint = {
            'trip': document['_id'],
            'event': {
                'location': updates.get('current_loc', document['current_loc']),
                'state': updates.get('state', document['state']),
            },
            'entity': 'passenger',
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

        # Update Trip stats from waypoint if is_active is updated from True to False
        if (updates.get('is_active') == False) and (document.get('is_active') == True):
            # waypoint = db['waypoint'].find_one({'trip': document['_id']}, sort=[('_created', -1)])
            waypoint = db['waypoint'].find_one({'_id': waypoint_id})
            # print(f"{waypoint=}")

            if waypoint is not None:
                res = db['passenger_trip'].update_one({'_id': document['_id']},
                                                        {
                                                            "$set": {
                                                                'stats': waypoint['cumulative_stats'],
                                                                'latest_waypoint': waypoint['_id']
                                                            }
                                                        })
