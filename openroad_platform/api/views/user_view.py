from http import HTTPStatus
from flask import current_app as app, Blueprint, request
from flask import abort, Response

# from api.utils import Status
# from api.models import UserStates
from api.controllers import UserController
from api.utils import patch_timestamps

# user_bp = Blueprint('user', __name__, url_prefix='/user/<_id>')


class UserView:
    """
    UserView provides hooks for handling user document insertion and updates in the API.

    Class Methods:
        on_insert(documents):
            Validates and processes user documents before insertion.
            - Validates each document using UserController.
            - If 'sim_clock' is present, sets '_created' and '_updated' timestamps accordingly.
            - Aborts with HTTP 403 if validation fails.

        on_update(updates, document):
            Validates and processes user documents before update.
            - Validates the update using UserController.
            - If 'sim_clock' is present in updates, sets '_updated' timestamp accordingly.
            - Aborts with HTTP 403 if validation fails.
    """

    @classmethod
    def on_insert(cls, documents):
        """
        Handles the insertion of new user documents.

        This method is called when new user documents are being inserted into the database.
        It validates each document using the UserController's validation logic. If a document
        contains a 'sim_clock' field, it sets the '_created' and '_updated' fields to the value
        of 'sim_clock'. If any exception occurs during processing, the request is aborted with
        a 403 status and the exception message.

        Args:
            documents (list): A list of user document dictionaries to be inserted.

        Raises:
            Aborts the request with a 403 status if validation fails or any exception occurs.
        """
        try:
            for document in documents:
                patch_timestamps(document)
                UserController.validate(document)
        except Exception as e:
            app.logger.error(f"Exception occurred: {e}")
            abort(Response(str(e), status=403))


    @classmethod
    def on_update(cls, updates, document):
        """
        Handles updates to a user document by validating the updates and setting the '_updated' field if 'sim_clock' is present.

        Args:
            updates (dict): The dictionary containing the fields to be updated.
            document (dict): The current state of the user document before updates.

        Raises:
            werkzeug.exceptions.HTTPException: If validation fails, aborts the request with a 403 status and logs the exception.
        """
        try:
            patch_timestamps(updates, update_only=True)
            UserController.validate(document, updates)
        except Exception as e:
            app.logger.error(f"Exception occurred: {e}")
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
