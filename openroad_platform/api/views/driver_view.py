from flask import current_app as app, Blueprint
from flask import abort, Response
import json
# from flask_jwt_extended import get_jwt, jwt_required
from bson.objectid import ObjectId

from api.utils import Status, patch_timestamps
from api.controllers import DriverController
from api.state_machine import RidehailDriverTripStateMachine

from eve.methods.get import get_internal
from eve.auth import auth_field_and_value



class DriverView:
    """
    DriverView provides API endpoints and hooks for managing driver resources in the OpenRoad platform.

    This class defines methods for validating and processing driver documents during insertion and update operations.
    It ensures that driver data adheres to business rules by leveraging the DriverController for validation.
    Special handling is provided for the 'sim_clock' field, which is used to set custom creation and update timestamps.

    Class Attributes:
        blueprint (Blueprint): Flask blueprint for driver-related routes.

    Class Methods:
        on_insert(documents):
            Validates and processes driver documents before insertion.
            Sets '_created' and '_updated' fields based on 'sim_clock' if present.
            Aborts with a 403 status code on validation failure or exception.

        on_update(updates, document):
            Validates updates to a driver document.
            Sets '_updated' field based on 'sim_clock' if present in updates.
            Aborts with a 403 status code on validation failure or exception.

    Note:
        Additional routes and hooks (such as pre_POST_callback and deregister) are present but commented out.
    """

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
        """
        Handles the insertion of driver documents into the database.

        Validates each document using DriverController.validate. If a document contains
        a 'sim_clock' field, sets the '_created' and '_updated' fields to its value.
        Aborts the operation with a 403 status code if any exception occurs during processing.

        Args:
            documents (list): List of driver documents to be inserted.

        Raises:
            Aborts the request with a 403 status code if validation fails or any exception occurs.
        """
        try:
            for document in documents:
                sim_clock = document.get('sim_clock')
                patch_timestamps(document)
                # Lookup id using statemachine name and domain
                statemachine = document.get('statemachine')
                if statemachine:
                    name = statemachine.get('name')
                    domain = statemachine.get('domain')
                    if name and domain:
                        db = app.data.driver.db
                        statemachine = db['statemachine'].find_one({'name': name, 'domain': domain})
                        if statemachine:
                            document['statemachine']['id'] = statemachine['_id']
                        else:
                            app.logger.warning(f"Statemachine not found for {name = }, {domain = }")

                DriverController.validate(document)

        except Exception as e:
            app.logger.error(f"Error updating driver document: {e}")
            abort(Response(f"An error occurred while updating the driver document: {str(e)}", status=403))


    @classmethod
    def on_update(cls, updates, document):
        """
        Handles updates to a driver document by validating the updates and setting the '_updated' field if 'sim_clock' is present.

        Args:
            updates (dict): Dictionary containing the fields to be updated.
            document (dict): The original driver document to be updated.

        Raises:
            abort: Aborts the request with a 403 status if validation fails or an exception occurs.
        """
        try:
            patch_timestamps(updates, update_only=True)
            DriverController.validate(document, updates)
        except Exception as e:
            app.logger.error(f"Error updating driver document: {e}")
            abort(Response(f"An error occurred while updating the driver document: {str(e)}", status=403))


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



