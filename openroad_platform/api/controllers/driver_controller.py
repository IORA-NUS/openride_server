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
        statemachine_id = (
            (updates.get('statemachine') or {}).get('id')
            or (document.get('statemachine') or {}).get('id')
            )
        if not statemachine_id:
            raise Exception("statemachine_id is required for dynamic loading.")

        from api.utils.state_machine_cache import get_state_machine, get_definition_func
        StateMachineClass = get_state_machine(statemachine_id, get_definition_func)
        machine = StateMachineClass(start_value=document['state'])
        transition = updates.get('transition')

        if transition is not None:
            if not isinstance(transition, str):
                raise Exception(f"Transition attribute must be a string, got {type(transition)}: {transition}")
            getattr(machine, transition)()

        updates['state'] = machine.current_state.name

