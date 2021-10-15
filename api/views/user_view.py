from http import HTTPStatus
from flask import current_app as app, Blueprint, request
from flask import abort, Response

# from api.utils import Status
# from api.models import UserStates
from api.controllers import UserController

# user_bp = Blueprint('user', __name__, url_prefix='/user/<_id>')


class UserView:
    ''' '''

    @classmethod
    def on_insert(cls, documents):
        ''' '''
        try:
            for document in documents:
                # UserStates.validate(document)
                UserController.validate(document)
                if document.get('sim_clock') is not None:
                    document['_created'] = document['sim_clock']
                    document['_updated'] = document['sim_clock']
        except Exception as e:
            abort(Response(str(e), status=403))


    @classmethod
    def on_update(cls, updates, document):
        ''' '''
        # print(f'inside userview.on_update')
        try:
            # UserStates.validate(document, updates)
            UserController.validate(document, updates)
            if updates.get('sim_clock') is not None:
                updates['_updated'] = updates['sim_clock']
        except Exception as e:
            abort(Response(str(e), status=403))



# @user_bp.route('assign_driver_vehicle', methods=['POST'])
# def assign_driver_vehicle(_id):
#     ''' '''
#     # print(request.json)
#     try:
#         UserController.assign_driver_vehicle(request.json.get('vehicle_id'), request.json.get('driver_id'))
#         return Response('Success', status=HTTPStatus.OK)
#     except Exception as e:
#         abort(Response(str(e), status=403))
