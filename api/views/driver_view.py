from flask import current_app as app, Blueprint
from flask import abort, Response
import json
# from flask_jwt_extended import get_jwt, jwt_required
from bson.objectid import ObjectId

from api.utils import Status
from api.controllers import DriverController
from api.state_machine import RidehailDriverTripStateMachine

from eve.methods.get import get_internal
from eve.auth import auth_field_and_value



class DriverView:
    ''' '''
    blueprint = Blueprint('driver', __name__, url_prefix='/driver')


    # @classmethod
    # def pre_POST_callback(cls, request):
    #     ''' '''
    #     db = app.data.driver.db
    #     driver = db['driver'].find_one({'user': get_jwt()[app.config["JWT_IDENTITY_CLAIM"]]})
    #     # print(driver)

    #     if driver is not None:
    #         abort(Response("Driver alredy exists", status=403))


    @classmethod
    def on_insert(cls, documents):
        ''' '''
        try:
            for document in documents:
                DriverController.validate(document)
                if document.get('sim_clock') is not None:
                    document['_created'] = document['sim_clock']
                    document['_updated'] = document['sim_clock']
        except Exception as e:
            abort(Response(str(e), status=403))


    @classmethod
    def on_update(cls, updates, document):
        ''' '''
        try:
            DriverController.validate(document, updates)
            if updates.get('sim_clock') is not None:
                updates['_updated'] = updates['sim_clock']
        except Exception as e:
            abort(Response(str(e), status=403))


    # @blueprint.route('/<id>/deregister', methods=['POST'])
    # @jwt_required()
    # def deregister(id):
    #     ''''''
    #     driver_resource = app.data.driver.db['driver']


    #     update_result = driver_resource.update_one({
    #         '_id': ObjectId(id),
    #         'user': get_jwt()[app.config["JWT_IDENTITY_CLAIM"]]
    #     },{
    #         '$set': {
    #             'status': Status.driver_dormant.value
    #         }
    #     })

    #     # return Response(driver, status=201)
    #     return update_result.raw_result, 201



