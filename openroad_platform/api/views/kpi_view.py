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

from eve.methods.get import get_internal
from eve.auth import auth_field_and_value

from datetime import date, datetime, tzinfo, timezone
from pymongo.cursor import CursorType



class KpiView:
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

        except Exception as e:
            abort(Response(str(e), status=403))



class KpiHistoryView(FlaskView):
    ''' '''
    route_prefix = '/<run_id>/kpi_history/<metric>'
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
