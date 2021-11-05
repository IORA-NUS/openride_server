from eve.methods.common import resolve_media_files
from flask import current_app as app
from flask import abort, Response
import json, pymongo
import haversine as hs


# from api.utils import Status
# from api.models import DriverStates, PassengerStates
from eve.methods.patch import patch_internal

class WaypointController:
    ''' '''
    @classmethod
    def update_stats(cls, document):
        ''' '''
        # print("indise WaypointController.update_stats")
        # print(document)
        trip = document['trip']
        # print(trip)

        waypoint_resource = app.data.driver.db['waypoint']
        # prev_waypoint = waypoint_resource.find_one({'trip': trip, '_created': {"$lt": document['_created']}})
        # prev_waypoint = waypoint_resource.find_one({'trip': trip,}, sort=[('_created', pymongo.DESCENDING)])
        prev_waypoint = waypoint_resource.find_one({
                                            'run_id': document['run_id'],
                                            'user': document['user'],
                                            'trip': trip,
                                        },
                                        sort=[('counter', pymongo.DESCENDING)]
                                    )

        # print(prev_waypoint)

        if prev_waypoint is not None:
            try:
                # print(prev_waypoint['event']['location']['coordinates'], document['event']['location']['coordinates'])
                distance = hs.haversine(prev_waypoint['event']['location']['coordinates'][:2], document['event']['location']['coordinates'][:2], unit=hs.Unit.METERS)
                # # print(f"document: {document}")
                # # print(f"prev_waypoint: {prev_waypoint}")

                duration = (document['_created'].replace(tzinfo=None) - prev_waypoint['_created'].replace(tzinfo=None)).total_seconds()
                # print(document['_created'], prev_waypoint['_created'].replace(tzinfo=None), duration)
                current_stats = {
                    'distance': distance,
                    'duration': duration,
                    'speed': (distance/duration) if (duration > 0) else 0
                }
                cumulative_stats = {
                    'distance': distance + prev_waypoint['cumulative_stats']['distance'],
                    'duration': duration + prev_waypoint['cumulative_stats']['duration'],
                    'speed': ((distance + prev_waypoint['cumulative_stats']['distance']) / (duration + prev_waypoint['cumulative_stats']['duration'])) if ((duration + prev_waypoint['cumulative_stats']['duration']) > 0) else 0
                }
            except Exception as e:
                print(e)
                raise e
        else:
            current_stats = {
                'distance': 0,
                'duration': 0,
                'speed': 0
            }
            cumulative_stats = {
                'distance': 0,
                'duration': 0,
                'speed': 0
            }


        # # print(current_stats, cumulative_stats )
        # # document['current_stats'] = current_stats
        # # document['cumulative_stats'] = cumulative_stats

        # try:
        #     res  = waypoint_resource.update_one({'_id': document['_id']}, {"$set": {'current_stats': current_stats, 'cumulative_stats': cumulative_stats}})
        #     # print(res.raw_result)
        # except Exception as e:
        #     # print(e)
        #     raise e
        # # print(document)
        # # print('end of update_stats')

        # # resp = patch_internal('waypoint', document)
        # # print(resp)

        document['current_stats'] = current_stats
        document['cumulative_stats'] = cumulative_stats
        document['counter'] = (prev_waypoint.get('counter', 0) + 1) if prev_waypoint is not None else 0
