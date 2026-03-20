from flask import current_app as app, Blueprint
from flask import abort, Response
import json
# from flask_jwt_extended import get_jwt, jwt_required
from bson.objectid import ObjectId

from api.utils import Status, patch_timestamps
from api.controllers import PassengerController

from eve.methods.get import get_internal
from eve.auth import auth_field_and_value



class PassengerView:
    """
    PassengerView handles API operations related to passenger resources.

    Class Attributes:
        blueprint (Blueprint): Flask blueprint for passenger-related routes.

    Class Methods:
        on_insert(documents):
            Validates and processes passenger documents before insertion.
            If 'sim_clock' is present in a document, sets '_created' and '_updated' fields accordingly.
            Aborts with status 403 if validation fails.

        on_update(updates, document):
            Validates and processes passenger documents before update.
            If 'sim_clock' is present in updates, sets '_updated' field accordingly.
            Aborts with status 403 if validation fails.

    Commented Methods:
        pre_POST_callback(request):
            (Commented out) Checks if a passenger already exists for the current user before POST.
            Aborts with status 403 if passenger exists.

        deregister(id):
            (Commented out) Deregisters a passenger by updating their status to dormant.
            Only allows the current user to deregister their own passenger resource.
    """

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
        """
        Handles the insertion of new passenger documents.

        Validates each document using the PassengerController. If the document contains a 'sim_clock' field,
        sets the '_created' and '_updated' fields to the value of 'sim_clock'. If any exception occurs during
        processing, aborts the request with a 403 status and the exception message.

        Args:
            documents (list): A list of passenger document dictionaries to be inserted.

        Raises:
            Aborts the request with a 403 status if validation or processing fails.
        """
        try:
            for document in documents:
                patch_timestamps(document)
                # Patch statemachine_id from statemachine lookup if needed
                statemachine = document.get('statemachine')
                if statemachine:
                    name = statemachine.get('name')
                    domain = statemachine.get('domain')
                    if name and domain:
                        db = app.data.driver.db
                        sm_doc = db['statemachine'].find_one({'name': name, 'domain': domain})
                        if sm_doc:
                            document['statemachine']['id'] = sm_doc['_id']
                        else:
                            app.logger.warning(f"Statemachine not found for {name = }, {domain = }")

                PassengerController.validate(document)
        except Exception as e:
            abort(Response(str(e), status=403))


    @classmethod
    def on_update(cls, updates, document):
        """
        Handles updates to a passenger document by validating the updates and setting the '_updated' field if 'sim_clock' is present.

        Args:
            updates (dict): The dictionary containing fields to update in the passenger document.
            document (dict): The current passenger document to be updated.

        Raises:
            Aborts the request with a 403 status code if validation fails or an exception occurs.
        """
        try:
            patch_timestamps(updates, update_only=True)
            PassengerController.validate(document, updates)
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



