
from flask import current_app as app
from flask import abort, Response
from eve.methods.post import post_internal
from eve.methods.patch import patch_internal

# from api.utils import Status
# from api.models import UserStates # , VehicleStates, DriverStates
from api.lib import UserStateMachine

class UserController:
    ''' '''

    @classmethod
    def validate(cls, document, updates={}):
        ''' '''
        # if updates is not None:
        if updates.get('transition') is not None:
            machine = UserStateMachine(start_value=document['state'])
            machine.run(updates.get('transition'))
            updates['state'] = machine.current_state.identifier


    # @classmethod
    # def assign_driver_vehicle(self, vehicle_id, driver_id):
    #     ''' '''
    #     try:
    #         print(vehicle_id, driver_id)
    #         # print(VehicleStates().offline.identifier)
    #         vehicle = app.data.find_one_raw('vehicle', _id=vehicle_id, state=VehicleStates().offline.identifier)
    #         # print(vehicle)
    #         driver = app.data.find_one_raw('driver', _id=driver_id)
    #         # print(driver)

    #         driver_set = set([]) if vehicle.get('driver_list') is None else set(vehicle.get('driver_list'))
    #         vehicle_set = set([]) if driver.get('vehicle_list') is None else set(driver.get('vehicle_list'))
    #         # print(driver_set, vehicle_set)

    #         try:
    #             driver_set.add(driver_id)
    #             vehicle_set.add(vehicle_id)
    #             # print(driver_set, vehicle_set)
    #         except Exception as e:
    #             print(e)
    #             raise(e)

    #         v_lookup = {'_id': vehicle_id}
    #         resp = patch_internal('vehicle', {'driver_list': list(driver_set)},  **v_lookup)

    #         d_lookup = {'_id': driver_id}
    #         resp = patch_internal('driver', {'vehicle_list': list(vehicle_set)},  **d_lookup)
    #         # print(resp)
    #         # print(vehicle, driver)

    #         # vehicle = Vehicle.objects.get(vehicle_id=vehicle_id, status=Status.vehicle_offline)
    #         # driver = Driver.objects.get(driver_id=driver_id)

    #         # Vehicle.objects(vehicle_id=vehicle_id).update_one(add_to_set__driver_list=driver)
    #         # Driver.objects(driver_id=driver_id).update_one(add_to_set__vehicle_list=vehicle)


    #     except Exception as e:
    #         raise e

