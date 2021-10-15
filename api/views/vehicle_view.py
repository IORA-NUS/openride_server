import re
from http import HTTPStatus
from flask import current_app as app, Blueprint
from flask import abort, Response, request
import json
# from flask_jwt_extended import get_jwt

from api.utils import Status
from api.controllers import VehicleController

# vehicle_bp = Blueprint('vehicle', __name__, url_prefix='/vehicle/<_id>')

class VehicleView:

    @classmethod
    def on_insert(cls, documents):
        ''' '''
        try:
            for document in documents:
                VehicleController.validate(document)
                if document.get('sim_clock') is not None:
                    document['_created'] = document['sim_clock']
                    document['_updated'] = document['sim_clock']
        except Exception as e:
            abort(Response(str(e), status=403))


    @classmethod
    def on_update(cls, updates, document):
        ''' '''
        try:
            VehicleController.validate(document, updates)
            if updates.get('sim_clock') is not None:
                updates['_updated'] = updates['sim_clock']
        except Exception as e:
            abort(Response(str(e), status=403))

        # updates['user'] = get_jwt()[app.config["JWT_IDENTITY_CLAIM"]]

        # # implement workflow decision tree
        # if updates.get('status') == Status.driver_dormant.value:
        #     updates['vehicle_list'] = []

# @vehicle_bp.route('add_driver', methods=['POST'])
# def assign_driver_vehicle(_id):
#     ''' '''
#     # print(request.json)
#     try:
#         VehicleController.add_driver(_id, request.json.get('driver_id'))
#         return Response('Success', status=HTTPStatus.OK)
#     except Exception as e:
#         abort(Response(str(e), status=403))
