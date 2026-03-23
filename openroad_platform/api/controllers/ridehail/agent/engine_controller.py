from flask import current_app as app
from flask import abort, Response, jsonify
import json
import traceback
import logging

# from api.utils import Status
# from api.models import DriverTripStates
from eve.methods.post import post, post_internal


class EngineController:
    """
    Controller class for managing engine-related operations.

    Methods
    -------
    add_history(document, updates=None):
        Adds a history record for the specified engine document.
        Parameters:
            document (dict): The engine document to record history for.
            updates (dict, optional): Additional updates to include in the history record.
        Raises:
            Exception: If an error occurs while posting the engine history or if the response structure is unexpected.
    """


    @classmethod
    def add_history(cls, document, updates=None):
        if updates is None:
            updates = {}

        db = app.data.driver.db

        engine_history = {
            'engine': document['_id'],
            'online_params': updates.get('online_params', document.get('online_params')),
            'runtime_performance': updates.get('last_run_performance')

        }

        if updates.get('sim_clock') is not None:
            engine_history['sim_clock'] = updates['sim_clock']
        elif document.get('sim_clock') is not None:
            engine_history['sim_clock'] = document['sim_clock']

        try:
            resp, *other_values =  post_internal('ridehail_engine_history', engine_history)
        except Exception as e:
            logging.error("An error occurred while adding engine history: %s", traceback.format_exc())

        # Handle both list and dict response types for _status check
        if isinstance(resp, list) and len(resp) > 0:
            status_obj = resp[0]
        elif isinstance(resp, dict):
            status_obj = resp
        else:
            raise Exception("Unexpected response structure: {}".format(resp))

        if '_status' in status_obj:
            if status_obj['_status'] == 'ERR':
                raise Exception(status_obj)
        else:
            raise Exception("_status not found in response: {}".format(resp))
