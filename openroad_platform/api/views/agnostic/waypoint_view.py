from flask import current_app as app, Blueprint
from flask import abort, Response, request, jsonify, Blueprint, make_response
import json
# from flask_jwt_extended import get_jwt, jwt_required
from bson.objectid import ObjectId
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

from api.config import simulation_domains


class WaypointView:
    """
    WaypointView handles operations related to waypoint documents in the API.

    Class Methods:
        on_insert(documents):
            Handles logic to be executed when a new waypoint document is inserted.
            - Sets '_created' and '_updated' fields based on 'sim_clock' if present.
            - Calls WaypointController.update_stats to update waypoint statistics.
            - Aborts with a 403 response if an exception occurs.

        # on_fetched(documents):
        #     (Commented out) Intended to handle logic after fetching waypoint documents.
    """

    @classmethod
    def on_insert(cls, documents):
        """
        Handles actions to perform when a new waypoint document is inserted.

        This method updates the '_created' and '_updated' fields of the document
        with the value of 'sim_clock' if it exists. If 'sim_clock' is not present,
        it logs a message indicating its absence. It then updates waypoint statistics
        using the WaypointController. If any exception occurs during the process,
        it aborts the request with a 403 status and the exception message.

        Args:
            documents (list): A list of documents being inserted. Only the first document is processed.

        Raises:
            Aborts the request with a 403 status if an exception occurs.
        """
        document = documents[0]
        try:
            # print('Updating Waypoint Stats on_insert()')
            if document.get('sim_clock') is not None:
                document['_created'] = document['sim_clock']
                document['_updated'] = document['sim_clock']
            else:
                # print("document.get('sim_clock') is None", document)
                app.logger.warning(f"sim_clock is missing from document: {document}")

            WaypointController.update_stats(document)
            # print(f"{document = }")
        except Exception as e:
            abort(Response(str(e), status=403))

    # @classmethod
    # def on_fetched(cls, documents):
    #     print(request.args)



class WaypointHistoryView(FlaskView):
    """
    WaypointHistoryView provides API endpoints to retrieve waypoint history data for trips.

    This view exposes endpoints to:
    - Retrieve waypoint paths for all trips within a specified time range.
    - Retrieve waypoint paths for a specific trip within a specified time range.

    Endpoints:
        - GET /<run_id>/waypoint_history/all_trips
            Returns waypoint paths for all trips between 'from' and 'to' datetime parameters (format: yyyymmddhhmmss).
        - GET /<run_id>/waypoint_history/trip/<trip>
            Returns waypoint paths for a specific trip (by trip ID) between 'from' and 'to' datetime parameters.

    Methods:
        - before_request: Initializes the database connection before handling requests.
        - path_from_all_trips: Handles requests for all trips' waypoint paths in the given time range.
        - path_from_trip: Handles requests for a specific trip's waypoint paths in the given time range.
        - get_paths_from_cursor: Helper method to query and format waypoint data from the database.

    Authentication:
        All endpoints require authentication with the 'waypoint' permission.

    Note:
        The time range for queries must be provided via 'from' and 'to' query parameters in the format yyyymmddhhmmss.
    """

    # route_prefix = '/<run_id>/waypoint_history'
    route_prefix = f"{simulation_domains['ridehail']}/<run_id>/waypoint_history"
    route_base = '/'
    decorators = [requires_auth('waypoint')]
    db = None


    def before_request(self, name, *args, **kwargs):
        ''' '''
        self.db = app.data.driver.db

    @route('/all_trips', methods=['GET'])
    def path_from_all_trips(self, **lookup): #run_id, _id):
        """
        Retrieve paths from all trips within a specified date range.

        This method extracts trip paths based on the provided lookup parameters,
        which should include 'from' and 'to' dates in the format 'yyyymmddhhmmss'.
        It fetches the relevant paths using these parameters and returns a JSON
        response containing the paths.

        Args:
            **lookup: Arbitrary keyword arguments containing filter parameters.
                Expected keys:
                    - 'from' (str): Start date in 'yyyymmddhhmmss' format.
                    - 'to' (str): End date in 'yyyymmddhhmmss' format.

        Returns:
            Response: A Flask response object with a JSON payload of the paths and HTTP status 200.
        """

        paths = self.get_paths_from_cursor(request.args, lookup)

        response = make_response(jsonify(paths), 200)

        return send_response('waypoint', response)

    @route('/trip/<trip>', methods=['GET'])
    def path_from_trip(self, **lookup): #run_id, _id):
        """
        Retrieves path information for a specific trip.

        Args:
            **lookup: Arbitrary keyword arguments containing trip lookup parameters.
                Required keys:
                    - 'trip': The trip identifier (will be converted to ObjectId).
                    - 'from': Start date/time in 'yyyymmddhhmmss' format.
                    - 'to': End date/time in 'yyyymmddhhmmss' format.

        Returns:
            Flask Response: A JSON response containing the paths for the specified trip.

        Summary:
            This method extracts path data for a trip using provided lookup parameters,
            formats the response as JSON, and sends it using a custom response handler.
        """

        lookup['trip'] = ObjectId(lookup['trip'])

        paths = self.get_paths_from_cursor(request.args, lookup)

        response = make_response(jsonify(paths), 200)

        return send_response('waypoint', response)



    def get_paths_from_cursor(self, args, filter):
        """
        Retrieves and processes waypoint documents from the database within a specified time range,
        grouping them by trip and trip state, and extracting relevant path, traversed path, and timestamp data.

        Args:
            args (dict): Dictionary containing 'from' and 'to' keys with datetime strings in '%Y%m%d%H%M%S' format,
                specifying the start and end of the time range for filtering waypoints.
            filter (dict): Additional MongoDB filter criteria to apply when querying waypoints.

        Returns:
            list: A list of dictionaries, each representing a trip segment with the following keys:
                - 'trip_id' (str): The unique identifier of the trip.
                - 'tripclass' (str/int): The state or class of the trip.
                - 'path' (list): List of [longitude, latitude] coordinates for the trip segment.
                - 'traversed_path' (list): List of traversed path coordinates for the trip segment.
                - 'timestamps' (list): List of seconds elapsed from the start time for each waypoint in the segment.
        """

        # print(args)
        _from = args.get('from')
        _to = args.get('to')

        if not _from:
            raise ValueError("The 'from' parameter is required and cannot be None.")
        if _to is None:
            raise ValueError("'to' parameter is required but not provided.")

        from_dt = datetime.strptime(_from, '%Y%m%d%H%M%S').replace(tzinfo=timezone.utc)
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
            "event.traversed_path": 1,
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
            'traversed_path': [],
            'timestamps': [],
        }
        paths = []
        for document in cursor:
            trip_id = str(document['trip'])
            coord = [round(x, 5) for x in document['event']['location']['coordinates']]
            traversed_path = document['event'].get('traversed_path') \
                                if document['event'].get('traversed_path') is not None \
                                else []

            tripclass = document['event'].get('state')
            if tripclass is None:
                app.logger.warning(f"'state' key is missing in event: {document['event']}")
                continue
            ts = document.get('_updated')
            if not isinstance(ts, datetime) or not isinstance(from_dt, datetime):
                app.logger.warning(f"Invalid datetime objects: ts={ts}, from_dt={from_dt}")
                continue

            if trip['trip_id'] is None:
                trip = {
                    'trip_id': trip_id,
                    'tripclass': tripclass,
                    'path': [coord],
                    'traversed_path': traversed_path,
                    'timestamps': [(ts-from_dt).seconds],
                }
            elif (trip['trip_id'] == trip_id) and (trip['tripclass'] == tripclass):
                trip['path'].append(coord)
                trip['traversed_path'].extend(traversed_path)
                trip['timestamps'].append((ts-from_dt).seconds)
            else:
                if len(trip['path']) > 1:
                    paths.append(trip)
                trip = {
                    'trip_id': trip_id,
                    'tripclass': tripclass,
                    'path': [coord],
                    'traversed_path': traversed_path,
                    'timestamps': [(ts-from_dt).seconds],
                }

        return paths
