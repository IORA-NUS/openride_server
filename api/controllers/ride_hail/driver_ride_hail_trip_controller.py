from flask import current_app as app
from flask import abort, Response, jsonify
import json, logging
import traceback

# from api.utils import Status
# from api.models import DriverTripStates
from eve.methods.post import post, post_internal
from api.state_machine import RidehailDriverTripStateMachine

class DriverRideHailTripStateMachine_Managed(RidehailDriverTripStateMachine):

    # def on_end_trip(self, doc):
    def on_end_trip(self, doc):
        doc['is_active'] = False

    def on_reject(self, doc):
        doc['is_active'] = False

    def on_cancel(self, doc):
        doc['is_active'] = False



class DriverRideHailTripController:
    ''' '''
    @classmethod
    def validate(cls, document, updates={}):
        ''' Additional validation checks and fields auto-added during pre_insert, pre_update hooks '''
        db = app.data.driver.db
        if updates != {}:
            # On Update
            # allow update only if trip is_active=True
            if document['is_active'] == False:
                # raise Exception('Cannot update when is_active is False')
                logging.info(f'Cannot update when is_active is False. DriverRideHailTripController', document['_id'], updates)

            # Update state
            try:
                machine = DriverRideHailTripStateMachine_Managed(start_value=document['state'])
                machine.run(updates.get('transition'), updates)
                updates['state'] = machine.current_state.identifier
                updates['feasible_transitions'] = [t.identifier for t in machine.current_state.transitions]
            except Exception as e:
                if updates.get('transition') is not None:
                    raise e

        else:
            # On Insert, check to ensure Only one active trip is allowed
            driver_ride_hail_trip = db['driver_ride_hail_trip'].find_one({'driver': document['driver'], 'is_active': True})

            if driver_ride_hail_trip is None:
                document['is_active'] = True
            else:
                raise Exception(f"Driver cannot have more than one active trip: {driver_ride_hail_trip['_id']}")


    @classmethod
    def add_waypoint(cls, document, updates={}):
        db = app.data.driver.db
        # print("inside add_waypoint")
        # print(updates)
        waypoint = {
            # 'trip': str(document['_id']),
            'trip': document['_id'],
            'event': {
                'location': updates.get('current_loc', document['current_loc']),
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
            # print(f"{resp[0]=}")
        except Exception as e:
            print(traceback.format_exc())

        if resp[0].get('_status') == 'ERR':
            raise Exception(resp[0])

        waypoint_id = resp[0]['_id']

        res = db['driver_ride_hail_trip'].update({'_id': document['_id']},
                                        {
                                            "$inc": {
                                                'num_waypoints': 1
                                            },
                                        })

        # Update Trip stats from waypoint if is_active is updated from True to False
        if (updates.get('is_active') == False) and (document.get('is_active') == True):
            # # waypoint = db['waypoint'].find_one({'trip': document['_id']}, sort=[('_created', -1)])
            waypoint = db['waypoint'].find_one({'_id': waypoint_id})
            # print(f"{waypoint=}")

            if waypoint is not None:
                res = db['driver_ride_hail_trip'].update({'_id': document['_id']},
                                                {
                                                    "$set": {
                                                        'stats': waypoint['cumulative_stats'],
                                                        'latest_waypoint': waypoint['_id']
                                                    },
                                                })

                # print(res)
