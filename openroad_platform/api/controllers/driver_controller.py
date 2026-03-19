from flask import current_app as app
from flask import abort, Response
import json

# from api.utils import Status
# from api.models import WorkflowStates
from api.state_machine import WorkflowStateMachine

class DriverController:
    """
    Controller class for handling driver-related operations within the OpenRoad platform.

    Methods
    -------
    validate(document, updates=None):
        Validates and updates the driver's document state based on provided transitions.
        Raises KeyError if the 'state' key is missing in the document.
    """

    # @classmethod
    # def check_license_uniqueness(cls, license_list):

    #     country_list = [item.get('country') for item in license_list]

    #     if len(country_list) > len(set(country_list)):
    #         raise Exception("Duplicate Licenses from Same country is not allowed")


    @classmethod
    def validate(cls, document, updates=None):
        ''' '''
        updates = updates or {}
        if updates.get('transition') is not None:
            if 'state' not in document:
                raise KeyError("The 'state' key is missing in the document.")

            machine = WorkflowStateMachine(start_value=document['state'])
            # machine.run(updates.get('transition'))
            getattr(machine, updates.get('transition'))()
            # check if transition occured else raise exception
            # if machine.current_state.name != document['state']:
            #     raise Exception(f"Transition '{updates.get('transition')}' did not occur. Current state: {machine.current_state.name}, {document['state'] =}")

            updates['state'] = machine.current_state.name

