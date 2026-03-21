from flask import current_app as app, Blueprint
from flask import abort, Response, request, jsonify, Blueprint, make_response
import json
import logging

# from flask_jwt_extended import get_jwt, jwt_required
from bson.objectid import ObjectId
from werkzeug.datastructures import MultiDict

from flask_classful import FlaskView, route
from eve.auth import requires_auth
from eve.utils import config
from eve.render import send_response

from api.utils import Status

from eve.methods.get import get_internal
from eve.auth import auth_field_and_value

from datetime import date, datetime, tzinfo, timezone
from pymongo.cursor import CursorType

from api.config import simulation_domains

class KpiView:
    """
    KpiView provides hooks for handling KPI (Key Performance Indicator) document insertions.

    Methods
    -------
    on_insert(cls, documents):
        Class method called when new KPI documents are inserted.
        For each document, if the 'sim_clock' field is present, sets the '_created' and '_updated'
        fields to the value of 'sim_clock'. If 'sim_clock' is missing, logs a message with the document.
    """
    ''' '''

    @classmethod
    def on_insert(cls, documents):
        """
        Handles the insertion of documents by setting the '_created' and '_updated' fields
        to the value of 'sim_clock' if it exists in each document. If 'sim_clock' is not present,
        logs a message indicating its absence.

        Args:
            documents (list): A list of document dictionaries to be inserted.

        Side Effects:
            Modifies each document in-place by adding or updating the '_created' and '_updated' fields.
            Prints a message to the console if 'sim_clock' is missing from a document.
        """
        ''' '''
        # document = documents[0]
        # try:
            # # print('Updating Waypoint Stats on_insert()')
            # if document.get('sim_clock') is not None:
            #     document['_created'] = document['sim_clock']
            #     document['_updated'] = document['sim_clock']
            # else:
            #     print("document.get('sim_clock') is None", document)

        # except Exception as e:
        #     abort(Response(str(e), status=403))
        for document in documents:
            if document.get('sim_clock', None) is not None:
                document['_created'] = document['sim_clock']
                document['_updated'] = document['sim_clock']
            else:
                app.logger.warning(f"sim_clock is missing from document: {document}")



class KpiHistoryView(FlaskView):
    """
    KpiHistoryView provides API endpoints for accessing KPI (Key Performance Indicator) history data for a given run and metric.

    Attributes:
        route_prefix (str): URL prefix for the KPI history endpoints, parameterized by run_id and metric.
        route_base (str): Base route for the view.
        decorators (list): List of decorators applied to all view methods, enforcing KPI-specific authentication.
        db: Database connection, initialized before each request.

    Methods:
        before_request(name, *args, **kwargs):
            Initializes the database connection before handling each request.

        # cumulative(**lookup):
        #     (Commented out) Intended to provide a summary of KPI data within a specified date range.

        # moving_average(**lookup):
        #     (Commented out) Intended to provide a moving average of KPI data within a specified date range.
    """

    # route_prefix = '/<run_id>/kpi_history/<metric>'
    route_prefix = f"{simulation_domains['ridehail']}/<run_id>/kpi_history/<metric>"
    route_base = '/'
    decorators = [requires_auth('kpi')]
    db = None


    def before_request(self, name, *args, **kwargs):
        ''' '''
        self.db = app.data.driver.db

    # @route('/cumulative', methods=['GET'])
    # def cumulative(self, **lookup): #run_id, _id):
    #     """The first line is the summary!

    #     lookup should have 'from' and 'to' dated in yyyymmddhhmmss

    #     """

    # @route('/moving_average', methods=['GET'])
    # def cumulative(self, **lookup): #run_id, _id):
    #     """The first line is the summary!

    #     lookup should have 'from' and 'to' dated in yyyymmddhhmmss

    #     """
