from flask import current_app as app
from flask import abort, Response
import json
import logging

from eve.methods.patch import patch_internal

# from api.utils import Status
# from api.models import WorkflowStates
# from api.state_machine import WorkflowStateMachine

class VehicleController:
    """
    Controller class for vehicle-related operations in the OpenRoad platform.

    Methods
    -------
    validate(document, updates=None):
        Validates and updates the workflow state of a vehicle document based on provided transitions.

    add_driver(vehicle_id, driver_id):
        Adds a driver to the authorised drivers list of a vehicle.

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


    @classmethod
    def add_driver(cls, vehicle_id, driver_id):
        ''' '''
        try:
            # print(vehicle_id, driver_id)
            # print(WorkflowStates().offline.name)
            vehicle = app.data.find_one_raw('vehicle', _id=vehicle_id)
            if vehicle is None:
                raise ValueError(f"Vehicle with ID {vehicle_id} does not exist.")
            # # print(vehicle)
            # driver = app.data.find_one_raw('driver', _id=driver_id)
            # # print(driver)

            driver_set = set([]) if vehicle.get('authorised_drivers') is None else set(vehicle.get('authorised_drivers'))
            # vehicle_set = set([]) if driver.get('vehicle_list') is None else set(driver.get('vehicle_list'))
            # print(driver_set, vehicle_set)

            try:
                driver_set.add(driver_id)
                # vehicle_set.add(vehicle_id)
                # print(driver_set, vehicle_set)
            except Exception as e:
                logging.error(f"An error occurred: {e}")
                raise(e)

            v_lookup = {'_id': vehicle_id}
            resp, *other_values = patch_internal('vehicle', {'authorised_drivers': list(driver_set)},  **v_lookup)

            # d_lookup = {'_id': driver_id}
            # resp = patch_internal('driver', {'vehicle_list': list(vehicle_set)},  **d_lookup)
            # print(resp)
            # print(vehicle, driver)

            # vehicle = Vehicle.objects.get(vehicle_id=vehicle_id, status=Status.vehicle_offline)
            # driver = Driver.objects.get(driver_id=driver_id)

            # Vehicle.objects(vehicle_id=vehicle_id).update_one(add_to_set__driver_list=driver)
            # Driver.objects(driver_id=driver_id).update_one(add_to_set__vehicle_list=vehicle)


        except Exception as e:
            logging.error(f"An error occurred in add_driver method: {e}")
            raise e

