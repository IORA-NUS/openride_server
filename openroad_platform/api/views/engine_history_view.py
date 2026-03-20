from flask import current_app as app, Blueprint
from flask import abort, Response
import json
# from flask_jwt_extended import get_jwt, jwt_required
from bson.objectid import ObjectId

from api.utils import Status
# from api.controllers import DriverController
from api.utils import patch_timestamps

from eve.methods.get import get_internal
from eve.auth import auth_field_and_value



class EngineHistoryView:
    """
    EngineHistoryView handles the insertion and update of engine history records.

    Class Attributes:
        blueprint (Blueprint): Flask Blueprint for engine history routes.

    Class Methods:
        on_insert(documents):
            Processes a list of documents before insertion. If a document contains a 'sim_clock' field,
            sets the '_created' and '_updated' fields to the value of 'sim_clock'. Aborts with a 403
            status if an exception occurs.

        on_update(updates, document):
            Processes updates to a document. If the updates contain a 'sim_clock' field,
            sets the '_updated' field to the value of 'sim_clock'. Aborts with a 403 status if an
            exception occurs.
    """

    blueprint = Blueprint('engine_history', __name__, url_prefix='/engine/<engine>/history')


    @classmethod
    def on_insert(cls, documents):
        """
        Handles the insertion of documents by setting the '_created' and '_updated' fields
        to the value of 'sim_clock' if it exists in each document.

        Args:
            documents (list): A list of dictionaries representing the documents to be inserted.

        Raises:
            werkzeug.exceptions.HTTPException: If an exception occurs during processing, aborts the request with a 403 status and the exception message.
        """
        try:
            for document in documents:
                patch_timestamps(document)
        except Exception as e:
            abort(Response(str(e), status=403))


    @classmethod
    def on_update(cls, updates, document):
        """
        Handles updates to a document by setting the '_updated' field to the value of 'sim_clock' if it exists in the updates.
        If an exception occurs during this process, aborts the request with a 403 status and the exception message.

        Args:
            updates (dict): Dictionary containing the fields to update.
            document (dict): The original document being updated.

        Raises:
            Aborts the request with a 403 status if an exception occurs.
        """
        try:
            patch_timestamps(updates, update_only=True)
        except Exception as e:
            abort(Response(str(e), status=403))



