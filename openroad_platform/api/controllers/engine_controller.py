from flask import current_app as app
from flask import abort, Response, jsonify
import json
import traceback

# from api.utils import Status
# from api.models import DriverTripStates
from eve.methods.post import post, post_internal


class EngineController:
    ''' '''

    @classmethod
    def add_history(cls, document, updates={}):
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
            resp =  post_internal('engine_history', engine_history)

        except Exception as e:
            print(traceback.format_exc())

        if resp[0].get('_status') == 'ERR':
            raise Exception(resp[0])
