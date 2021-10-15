from flask import current_app as app
from flask import abort, Response
import json

# from api.utils import Status
# from api.models import WorkflowStates
from api.lib import WorkflowStateMachine

class DriverController:
    ''' '''

    # @classmethod
    # def check_license_uniqueness(cls, license_list):

    #     country_list = [item.get('country') for item in license_list]

    #     if len(country_list) > len(set(country_list)):
    #         raise Exception("Duplicate Licenses from Same country is not allowed")


    @classmethod
    def validate(cls, document, updates={}):
        ''' '''
        if updates.get('transition') is not None:
            machine = WorkflowStateMachine(start_value=document['state'])
            machine.run(updates.get('transition'))
            updates['state'] = machine.current_state.identifier

