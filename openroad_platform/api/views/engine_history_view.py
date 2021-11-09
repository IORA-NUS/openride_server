from flask import current_app as app, Blueprint
from flask import abort, Response
import json
# from flask_jwt_extended import get_jwt, jwt_required
from bson.objectid import ObjectId

from api.utils import Status
# from api.controllers import DriverController

from eve.methods.get import get_internal
from eve.auth import auth_field_and_value



class EngineHistoryView:
    ''' '''
    blueprint = Blueprint('engine_history', __name__, url_prefix='/engine/<engine>/history')


    @classmethod
    def on_insert(cls, documents):
        ''' '''
        try:
            for document in documents:
                if document.get('sim_clock') is not None:
                    document['_created'] = document['sim_clock']
                    document['_updated'] = document['sim_clock']
        except Exception as e:
            abort(Response(str(e), status=403))


    @classmethod
    def on_update(cls, updates, document):
        ''' '''
        try:
            if updates.get('sim_clock') is not None:
                updates['_updated'] = updates['sim_clock']
        except Exception as e:
            abort(Response(str(e), status=403))



