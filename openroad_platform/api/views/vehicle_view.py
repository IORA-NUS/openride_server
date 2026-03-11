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
    """
    VehicleView provides hooks for handling insert and update operations on vehicle documents.

    Class Methods:
    --------------
    on_insert(cls, documents):
        Validates each document before insertion using VehicleController.
        If 'sim_clock' is present in a document, sets '_created' and '_updated' fields to its value.
        Logs and aborts with a 403 status on validation or processing errors.

    on_update(cls, updates, document):
        Validates updates to a document using VehicleController.
        If 'sim_clock' is present in updates, sets '_updated' field to its value.
        Logs and aborts with a 403 status on validation or processing errors.
    """

    @classmethod
    def on_insert(cls, documents):
        """
        Handles the insertion of new vehicle documents into the database.

        Validates each document using the VehicleController. If a document contains a 'sim_clock' field,
        sets the '_created' and '_updated' fields to the value of 'sim_clock'. Logs and aborts the request
        with a 403 status code if any exception occurs during processing.

        Args:
            documents (list): A list of dictionaries representing vehicle documents to be inserted.

        Raises:
            abort: Aborts the request with a 403 status code if validation or processing fails.
        """
        try:
            for document in documents:
                VehicleController.validate(document)
                if document.get('sim_clock') is not None:
                    document['_created'] = document['sim_clock']
                    document['_updated'] = document['sim_clock']
        except Exception as e:
            app.logger.error(f"Exception occurred: {e}")
            abort(Response(str(e), status=403))


    @classmethod
    def on_update(cls, updates, document):
        """
        Handles updates to a vehicle document by validating the updates and applying specific logic.

        Args:
            updates (dict): The dictionary containing fields to be updated in the vehicle document.
            document (dict): The current state of the vehicle document before updates.

        Raises:
            werkzeug.exceptions.HTTPException: If validation fails or an exception occurs, aborts the request with a 403 status and logs the error.

        Side Effects:
            - Calls VehicleController.validate to ensure updates are valid.
            - If 'sim_clock' is present in updates, sets '_updated' to its value.
            - Logs any exceptions that occur during processing.
        """
        try:
            VehicleController.validate(document, updates)
            if updates.get('sim_clock') is not None:
                updates['_updated'] = updates['sim_clock']
        except Exception as e:
            app.logger.error(f"Exception occurred: {e}")
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
