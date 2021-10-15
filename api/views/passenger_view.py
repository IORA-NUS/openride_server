from flask import current_app as app, Blueprint
from flask import abort, Response
import json
# from flask_jwt_extended import get_jwt, jwt_required
from bson.objectid import ObjectId

from api.utils import Status
from api.controllers import PassengerController

from eve.methods.get import get_internal
from eve.auth import auth_field_and_value



class PassengerView:
    ''' '''
    blueprint = Blueprint('passenger', __name__, url_prefix='/passenger')


    # @classmethod
    # def pre_POST_callback(cls, request):
    #     ''' '''
    #     db = app.data.driver.db
    #     passenger = db['passenger'].find_one({'user': get_jwt()[app.config["JWT_IDENTITY_CLAIM"]]})
    #     # print(passenger)

    #     if passenger is not None:
    #         abort(Response("Passenger alredy exists", status=403))


    @classmethod
    def on_insert(cls, documents):
        ''' '''
        try:
            for document in documents:
                PassengerController.validate(document)
                if document.get('sim_clock') is not None:
                    document['_created'] = document['sim_clock']
                    document['_updated'] = document['sim_clock']
        except Exception as e:
            abort(Response(str(e), status=403))


    @classmethod
    def on_update(cls, updates, document):
        ''' '''
        try:
            PassengerController.validate(document, updates)
            if updates.get('sim_clock') is not None:
                updates['_updated'] = updates['sim_clock']
        except Exception as e:
            abort(Response(str(e), status=403))


    # @blueprint.route('/<id>/deregister', methods=['POST'])
    # @jwt_required()
    # def deregister(id):
    #     ''''''
    #     passenger_resource = app.data.passenger.db['passenger']


    #     update_result = passenger_resource.update_one({
    #         '_id': ObjectId(id),
    #         'user': get_jwt()[app.config["JWT_IDENTITY_CLAIM"]]
    #     },{
    #         '$set': {
    #             'status': Status.passenger_dormant.value
    #         }
    #     })

    #     # return Response(passenger, status=201)
    #     return update_result.raw_result, 201



