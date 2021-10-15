from flask import current_app as app, Blueprint
from flask import abort, Response, request, jsonify, Blueprint, make_response
import json
# from flask_jwt_extended import get_jwt, jwt_required
from bson.objectid import ObjectId
from numpy.lib.twodim_base import tri
from werkzeug.datastructures import MultiDict

from flask_classful import FlaskView, route
from eve.auth import requires_auth
from eve.utils import config
from eve.render import send_response

from api.utils import Status
from api.controllers import WaypointController

from eve.methods.get import get_internal
from eve.auth import auth_field_and_value

from datetime import date, datetime, tzinfo, timezone
from pymongo.cursor import CursorType



class WaypointView:
    ''' '''

    @classmethod
    def on_insert(cls, documents):
        ''' '''
        document = documents[0]
        try:
            # print('Updating Waypoint Stats on_insert()')
            if document.get('sim_clock') is not None:
                document['_created'] = document['sim_clock']
                document['_updated'] = document['sim_clock']
            else:
                print("document.get('sim_clock') is None", document)

            WaypointController.update_stats(document)
            # print(f"{document = }")
        except Exception as e:
            abort(Response(str(e), status=403))

    @classmethod
    def on_fetched(cls, documents):
        print(request.args)



class WaypointHistoryView(FlaskView):
    ''' '''
    route_prefix = '/<run_id>/waypoint_history'
    route_base = '/'
    decorators = [requires_auth('waypoint')]
    db = None


    def before_request(self, name, *args, **kwargs):
        ''' '''
        self.db = app.data.driver.db

    @route('/all_trips', methods=['GET'])
    def path_from_all_trips(self, **lookup): #run_id, _id):
        """The first line is the summary!

        lookup should have 'from' and 'to' dated in yyyymmddhhmmss

        """

        paths = self.get_paths_from_cursor(request.args, lookup)

        response = make_response(jsonify(paths), 200)

        return send_response('waypoint', response)

    @route('/trip/<trip>', methods=['GET'])
    def path_from_trip(self, **lookup): #run_id, _id):
        """The first line is the summary!

        lookup should have 'from' and 'to' dated in yyyymmddhhmmss

        """
        lookup['trip'] = ObjectId(lookup['trip'])

        paths = self.get_paths_from_cursor(request.args, lookup)

        response = make_response(jsonify(paths), 200)

        return send_response('waypoint', response)



    def get_paths_from_cursor(self, args, filter):

        # print(args)
        _from = args.get('from')
        from_dt = datetime.strptime(_from, '%Y%m%d%H%M%S').replace(tzinfo=timezone.utc)
        _to = args.get('to')
        to_dt = datetime.strptime(_to, '%Y%m%d%H%M%S').replace(tzinfo=timezone.utc)

        filter["_updated"] = {
            "$gte": from_dt,
            "$lt": to_dt
        }
        # print(filter)
        project = {
            '_id': 0,
            "event.state": 1,
            "event.location.coordinates": 1,
            "trip": 1,
            "_updated": 1,
        }
        sort=list({
            'trip': 1,
            'counter': 1
        }.items())

        cursor = self.db['waypoint'].find(
            filter=filter,
            projection=project,
            sort=sort,
            cursor_type=CursorType.EXHAUST
        )

        trip = {
            'trip_id': None,
            'tripclass': None,
            'path': [],
            'timestamps': [],
        }
        paths = []
        for document in cursor:
            trip_id = str(document['trip'])
            coord = [round(x, 5) for x in document['event']['location']['coordinates']]
            tripclass = document['event']['state']
            ts = document['_updated']

            if trip['trip_id'] is None:
                trip = {
                    'trip_id': trip_id,
                    'tripclass': tripclass,
                    'path': [coord],
                    'timestamps': [(ts-from_dt).seconds],
                }
            elif (trip['trip_id'] == trip_id) and (trip['tripclass'] == tripclass):
                trip['path'].append(coord)
                trip['timestamps'].append((ts-from_dt).seconds)
            else:
                if len(trip['path']) > 1:
                    paths.append(trip)
                trip = {
                    'trip_id': trip_id,
                    'tripclass': tripclass,
                    'path': [coord],
                    'timestamps': [(ts-from_dt).seconds],
                }

        return paths
