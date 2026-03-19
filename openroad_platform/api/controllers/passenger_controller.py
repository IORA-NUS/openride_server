from flask import current_app as app
from flask import abort, Response
import json

# from api.utils import Status
# from api.models import WorkflowStates

from api.state_machine import WorkflowStateMachine

class PassengerController:
    """
    PassengerController provides methods for validating passenger-related data and managing workflow state transitions.

    Methods
    -------
    validate(document, updates={}):
        Validates and updates the state of a passenger document based on workflow transitions.
        If a 'transition' is specified in updates, it uses WorkflowStateMachine to process the transition and update the document's state.

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
        # if updates is not None:
        if updates.get('transition') is not None:
            if 'state' not in document:
                raise KeyError("The 'state' key is missing in the document.")

            machine = WorkflowStateMachine(start_value=document['state'])
            # machine.run(updates.get('transition'))
            getattr(machine, updates.get('transition'))()

            updates['state'] = machine.current_state.name

