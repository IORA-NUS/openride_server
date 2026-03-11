from flask import current_app as app, Blueprint
from flask import abort, Response
import json
# from flask_jwt_extended import get_jwt, jwt_required
from bson.objectid import ObjectId

from api.utils import Status
from api.controllers import EngineController

from eve.methods.get import get_internal
from eve.auth import auth_field_and_value



class EngineView:
    """
    EngineView provides class methods to handle insert and update events for engine-related resources.

    Class Attributes:
        blueprint (Blueprint): Flask Blueprint for engine API endpoints.

    Class Methods:
        on_insert(documents):
            Handles logic before inserting new documents.
            If 'sim_clock' is present in a document, sets '_created' and '_updated' fields to its value.
            Aborts with HTTP 403 on error.

        on_update(updates, document):
            Handles logic before updating a document.
            If 'sim_clock' is present in updates, sets '_updated' to its value.
            Aborts with HTTP 403 on error.

        on_updated(updates, document):
            Handles logic after a document has been updated.
            Calls EngineController.add_history to record the update.
            Aborts with HTTP 403 on error.
    """

    blueprint = Blueprint('engine', __name__, url_prefix='/engine')


    @classmethod
    def on_insert(cls, documents):
        """
        Handles the insertion of documents by setting '_created' and '_updated' fields to the value of 'sim_clock' if present.

        Args:
            documents (list): A list of document dictionaries to be inserted.

        Raises:
            werkzeug.exceptions.HTTPException: If an exception occurs during processing, aborts the request with a 403 status and the exception message.
        """

        try:
            for document in documents:
                if document.get('sim_clock', None) is not None:
                    document['_created'] = document['sim_clock']
                    document['_updated'] = document['sim_clock']
        except Exception as e:
            abort(Response(str(e), status=403))


    @classmethod
    def on_update(cls, updates, document):
        """
        Handles updates to a document by checking for the presence of a 'sim_clock' key in the updates dictionary.
        If 'sim_clock' is present, sets the '_updated' field in updates to the value of 'sim_clock'.
        Aborts the request with a 403 status code if an exception occurs.

        Args:
            updates (dict): Dictionary containing fields to update in the document.
            document (dict): The original document being updated.

        Raises:
            abort: Aborts the request with a 403 status code and the exception message if an error occurs.
        """
        try:
            if updates.get('sim_clock', None) is not None:
                updates['_updated'] = updates['sim_clock']
        except Exception as e:
            abort(Response(str(e), status=403))

    @classmethod
    def on_updated(cls, updates, document):
        """
        Handles updates to a document by recording the changes in the engine history.

        Args:
            updates (dict): The updates applied to the document.
            document (dict): The original document being updated.

        Raises:
            HTTPException: Returns a 403 response if an error occurs while adding history.
        """

        try:
            EngineController.add_history(document, updates)
        except Exception as e:
            print(f"Error in on_updated: {e}")
            abort(Response(str(e), status=403))

