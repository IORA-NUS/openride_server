from api.state_machine import RidehailPassengerTripStateMachine
from flask import current_app as app, Blueprint
from flask import abort, Response, make_response, request
from flask_classful import FlaskView, route

import json, traceback
# from flask_jwt_extended import get_jwt, jwt_required, verify_jwt_in_request
from bson.objectid import ObjectId

from api.utils import Status
from api.controllers import PassengerRideHailTripController

from eve.methods.get import get_internal
from eve.methods.patch import patch_internal
from eve.auth import auth_field_and_value, requires_auth
from eve.utils import config
from eve.render import send_response




class PassengerRideHailTripView:
    ''' '''

    @classmethod
    def on_insert(cls, documents):
        ''' '''
        if len(documents) > 1:
            abort(Response("Insert accepts only a single item", status=403))

        document = documents[0]
        # print(f"inside PassengerTripView.on_insert, {document.get('sim_clock') = }")
        try:
            PassengerRideHailTripController.validate(document)
            if document.get('sim_clock') is not None:
                document['_created'] = document['sim_clock']
                document['_updated'] = document['sim_clock']
        except Exception as e:
            abort(Response(str(e), status=403))


    @classmethod
    def on_update(cls, updates, document):
        ''' '''
        # print(f"inside PassengerTripView.on_update, {document.get('sim_clock') = }")
        try:
            # print('validating before update PassengerTripView')
            PassengerRideHailTripController.validate(document, updates)
            if updates.get('sim_clock') is not None:
                updates['_updated'] = updates['sim_clock']
        except Exception as e:
            print(traceback.format_exc())
            abort(Response(str(e), status=403))


    @classmethod
    def on_inserted(cls, documents):
        ''' '''
        document = documents[0]
        try:
            PassengerRideHailTripController.add_waypoint(document)
        except Exception as e:
            abort(Response(str(e), status=403))


    @classmethod
    def on_updated(cls, updates, document):
        ''' '''
        try:
            PassengerRideHailTripController.add_waypoint(document, updates)
        except Exception as e:
            abort(Response(str(e), status=403))

class PassengerRideHailTripWorkflowView(FlaskView):
    ''' '''
    route_prefix = '/<run_id>/passenger/ride_hail/trip/<_id>'
    route_base = '/'
    decorators = [requires_auth('passenger_ride_hail_trip')]


    def before_patch(self, name, *args, **kwargs):
        ''' '''
        # db = app.data.driver.db
        if config.IF_MATCH:
            kwargs[config.ETAG] = request.headers['If-Match']

        # verify_jwt_in_request()
        # id_payload = get_jwt()[app.config["JWT_IDENTITY_CLAIM"]]
        # # kwargs[app.config["AUTH_FIELD"]] = id_payload['_id']
        # print(f"{name=}, {args=}, {kwargs=}")

        if name in []:  # NOTE Include validation for all methods that use POST / PUT
            document = request.json
            PassengerRideHailTripController.validate(document)
        else: # NOTE Include validation for all methods that use PATCH
            response = get_internal('passenger_ride_hail_trip', **kwargs)
            # print(response[0])
            document = response[0]['_items'][0] # Raises exception if document is not found.
            updates = request.json
            PassengerRideHailTripController.validate(document, updates)

        # print(f"{request.json.get('sim_clock')=}")
        if request.json.get('sim_clock') is not None:
            if name in []:
                request.json['_created'] = request.json['sim_clock']

            request.json['_updated'] = request.json['sim_clock']
        else:
            print("Missing Sim_clock")


    @route('/<transition>', methods=['PATCH'])
    def patch_transition(self, **lookup): #run_id, _id):
        """End an active Driver-Trip
        ---
        patch:
        description: Update trip and set state to Complete with provision for force_quit.
        if force_quit is false, The endpoint validates State Transition
        security:
            - ApiKeyAuth: []
        responses:
            200:
            content:
                application/json:
                schema: PetSchema

        """
        if config.IF_MATCH:
            lookup[config.ETAG] = request.headers['If-Match']

        payload = request.json
        payload['transition'] = lookup.pop('transition')
        if payload['transition'] == 'force_quit':
            payload['force_quit'] =  True


        response = patch_internal('passenger_ride_hail_trip',
                                    skip_validation=True, # Done to ensure sim_clock is updatable
                                    payload=payload,
                                    **lookup
                                )
        return send_response('passenger_ride_hail_trip', response)

    @route('/state/<state>', methods=['GET'])
    def list_by_state(self, **lookup): #run_id, _id):
        """The first line is the summary!

        All the rest goes in the description.

        """
        db = app.data.driver.db
        projection = json.loads(request.args.get('projection'))
        # print(projection)

        cursor = db['passenger_ride_hail_trip'].find(
            lookup,
            projection=projection
        )

        # return jsonify(data), 200
        return send_response('passenger_ride_hail_trip', (list(cursor), None, None, 200, []))



# class PassengerRideHailTripWorkflowView(FlaskView):
#     ''' '''
#     route_prefix = '/<run_id>/passenger/ride_hail/trip/<_id>'
#     route_base = '/'
#     decorators = [requires_auth('passenger_ride_hail_trip')]


#     def before_request(self, name, *args, **kwargs):
#         ''' '''
#         # db = app.data.driver.db
#         if config.IF_MATCH:
#             kwargs[config.ETAG] = request.headers['If-Match']

#         # verify_jwt_in_request()
#         # id_payload = get_jwt()[app.config["JWT_IDENTITY_CLAIM"]]
#         # # kwargs[app.config["AUTH_FIELD"]] = id_payload['_id']
#         # print(f"{name=}, {args=}, {kwargs=}")

#         if name in []:  # NOTE Include validation for all methods that use POST / PUT
#             document = request.json
#             PassengerRideHailTripController.validate(document)
#         else: # NOTE Include validation for all methods that use PATCH
#             response = get_internal('passenger_ride_hail_trip', **kwargs)
#             # print(response[0])
#             document = response[0]['_items'][0] # Raises exception if document is not found.
#             updates = request.json
#             PassengerRideHailTripController.validate(document, updates)

#         # print(f"{request.json.get('sim_clock')=}")
#         if request.json.get('sim_clock') is not None:
#             if name in []:
#                 request.json['_created'] = request.json['sim_clock']

#             request.json['_updated'] = request.json['sim_clock']
#         else:
#             print("Missing Sim_clock")


#     @route('/assign', methods=['PATCH'])
#     def assign(self, **lookup): #run_id, _id):
#         """End an active Driver-Trip
#         ---
#         patch:
#         description: Update trip and set state to Complete with provision for force_quit.
#         if force_quit is false, The endpoint validates State Transition
#         security:
#             - ApiKeyAuth: []
#         responses:
#             200:
#             content:
#                 application/json:
#                 schema: PetSchema

#         """
#         if config.IF_MATCH:
#             lookup[config.ETAG] = request.headers['If-Match']
#         # print(lookup)

#         payload = request.json
#         payload['transition'] =  RidehailPassengerTripStateMachine.assign.identifier

#         response = patch_internal('passenger_ride_hail_trip',
#                                     skip_validation=True, # Done to ensure sim_clock is updatable
#                                     payload=payload,
#                                     **lookup
#                                 )
#         return send_response('passenger_ride_hail_trip', response)

#     @route('/accept', methods=['PATCH'])
#     def accept(self, **lookup): #run_id, _id):
#         """End an active Driver-Trip
#         ---
#         patch:
#         description: Update trip and set state to Complete with provision for force_quit.
#         if force_quit is false, The endpoint validates State Transition
#         security:
#             - ApiKeyAuth: []
#         responses:
#             200:
#             content:
#                 application/json:
#                 schema: PetSchema

#         """
#         if config.IF_MATCH:
#             lookup[config.ETAG] = request.headers['If-Match']
#         # print(lookup)

#         payload = request.json

#         payload['transition'] =  RidehailPassengerTripStateMachine.accept.identifier

#         response = patch_internal('passenger_ride_hail_trip',
#                                     skip_validation=True, # Done to ensure sim_clock is updatable
#                                     payload=payload,
#                                     **lookup
#                                 )
#         return send_response('passenger_ride_hail_trip', response)

#     @route('/reject', methods=['PATCH'])
#     def reject(self, **lookup): #run_id, _id):
#         """End an active Driver-Trip
#         ---
#         patch:
#         description: Update trip and set state to Complete with provision for force_quit.
#         if force_quit is false, The endpoint validates State Transition
#         security:
#             - ApiKeyAuth: []
#         responses:
#             200:
#             content:
#                 application/json:
#                 schema: PetSchema

#         """
#         if config.IF_MATCH:
#             lookup[config.ETAG] = request.headers['If-Match']
#         # print(lookup)

#         payload = request.json

#         payload['transition'] =  RidehailPassengerTripStateMachine.reject.identifier

#         response = patch_internal('passenger_ride_hail_trip',
#                                     skip_validation=True, # Done to ensure sim_clock is updatable
#                                     payload=payload,
#                                     **lookup
#                                 )
#         return send_response('passenger_ride_hail_trip', response)

#     @route('/cancel', methods=['PATCH'])
#     def cancel(self, **lookup): #run_id, _id):
#         """End an active Driver-Trip
#         ---
#         patch:
#         description: Update trip and set state to Complete with provision for force_quit.
#         if force_quit is false, The endpoint validates State Transition
#         security:
#             - ApiKeyAuth: []
#         responses:
#             200:
#             content:
#                 application/json:
#                 schema: PetSchema

#         """
#         if config.IF_MATCH:
#             lookup[config.ETAG] = request.headers['If-Match']
#         # print(lookup)

#         payload = request.json
#         payload['transition'] =  RidehailPassengerTripStateMachine.cancel.identifier
#         # print(f"{payload=}")

#         response = patch_internal('passenger_ride_hail_trip',
#                                     skip_validation=True, # Done to ensure sim_clock is updatable
#                                     payload=payload,
#                                     **lookup
#                                 )
#         # print(response)
#         return send_response('passenger_ride_hail_trip', response)

#     @route('/driver_confirmed_trip', methods=['PATCH'])
#     def driver_confirmed_trip(self, **lookup): #run_id, _id):
#         """End an active Driver-Trip
#         ---
#         patch:
#         description: Update trip and set state to Complete with provision for force_quit.
#         if force_quit is false, The endpoint validates State Transition
#         security:
#             - ApiKeyAuth: []
#         responses:
#             200:
#             content:
#                 application/json:
#                 schema: PetSchema

#         """
#         if config.IF_MATCH:
#             lookup[config.ETAG] = request.headers['If-Match']
#         # print(lookup)

#         payload = request.json

#         payload['transition'] =  RidehailPassengerTripStateMachine.driver_confirmed_trip.identifier

#         response = patch_internal('passenger_ride_hail_trip',
#                                     skip_validation=True, # Done to ensure sim_clock is updatable
#                                     payload=payload,
#                                     **lookup
#                                 )
#         return send_response('passenger_ride_hail_trip', response)

#     @route('/wait_for_pickup', methods=['PATCH'])
#     def wait_for_pickup(self, **lookup): #run_id, _id):
#         """End an active Driver-Trip
#         ---
#         patch:
#         description: Update trip and set state to Complete with provision for force_quit.
#         if force_quit is false, The endpoint validates State Transition
#         security:
#             - ApiKeyAuth: []
#         responses:
#             200:
#             content:
#                 application/json:
#                 schema: PetSchema

#         """
#         if config.IF_MATCH:
#             lookup[config.ETAG] = request.headers['If-Match']
#         # print(lookup)

#         payload = request.json

#         payload['transition'] =  RidehailPassengerTripStateMachine.wait_for_pickup.identifier

#         # print(f"{payload=}")

#         response = patch_internal('passenger_ride_hail_trip',
#                                     skip_validation=True, # Done to ensure sim_clock is updatable
#                                     payload=payload,
#                                     **lookup
#                                 )
#         return send_response('passenger_ride_hail_trip', response)

#     @route('/driver_cancelled_trip', methods=['PATCH'])
#     def driver_cancelled_trip(self, **lookup): #run_id, _id):
#         """End an active Driver-Trip
#         ---
#         patch:
#         description: Update trip and set state to Complete with provision for force_quit.
#         if force_quit is false, The endpoint validates State Transition
#         security:
#             - ApiKeyAuth: []
#         responses:
#             200:
#             content:
#                 application/json:
#                 schema: PetSchema

#         """
#         if config.IF_MATCH:
#             lookup[config.ETAG] = request.headers['If-Match']
#         # print(lookup)

#         payload = request.json

#         payload['transition'] =  RidehailPassengerTripStateMachine.driver_cancelled_trip.identifier

#         response = patch_internal('passenger_ride_hail_trip',
#                                     skip_validation=True, # Done to ensure sim_clock is updatable
#                                     payload=payload,
#                                     **lookup
#                                 )
#         return send_response('passenger_ride_hail_trip', response)

#     @route('/driver_arrived_for_pickup', methods=['PATCH'])
#     def driver_arrived_for_pickup(self, **lookup): #run_id, _id):
#         """End an active Driver-Trip
#         ---
#         patch:
#         description: Update trip and set state to Complete with provision for force_quit.
#         if force_quit is false, The endpoint validates State Transition
#         security:
#             - ApiKeyAuth: []
#         responses:
#             200:
#             content:
#                 application/json:
#                 schema: PetSchema

#         """
#         if config.IF_MATCH:
#             lookup[config.ETAG] = request.headers['If-Match']
#         # print(lookup)

#         # # compute passenger waiting time
#         # lookup_trip_request_waypoint = {
#         #     'run_id': lookup['run_id'],
#         #     'trip': lookup['_id'],

#         # }
#         # waypoint_response = get_internal('waypoint', **lookup_trip_request_waypoint)
#         # if waypoint_response[3] <= 299: # Faux is success
#         #     ''' '''

#         payload = request.json

#         payload['transition'] =  RidehailPassengerTripStateMachine.driver_arrived_for_pickup.identifier

#         response = patch_internal('passenger_ride_hail_trip',
#                                     skip_validation=True, # Done to ensure sim_clock is updatable
#                                     payload=payload,
#                                     **lookup
#                                 )
#         return send_response('passenger_ride_hail_trip', response)

#     @route('/driver_move_for_dropoff', methods=['PATCH'])
#     def driver_move_for_dropoff(self, **lookup): #run_id, _id):
#         """End an active Driver-Trip
#         ---
#         patch:
#         description: Update trip and set state to Complete with provision for force_quit.
#         if force_quit is false, The endpoint validates State Transition
#         security:
#             - ApiKeyAuth: []
#         responses:
#             200:
#             content:
#                 application/json:
#                 schema: PetSchema

#         """
#         if config.IF_MATCH:
#             lookup[config.ETAG] = request.headers['If-Match']
#         # print(lookup)

#         payload = request.json

#         payload['transition'] =  RidehailPassengerTripStateMachine.driver_move_for_dropoff.identifier

#         response = patch_internal('passenger_ride_hail_trip',
#                                     skip_validation=True, # Done to ensure sim_clock is updatable
#                                     payload=payload,
#                                     **lookup
#                                 )
#         return send_response('passenger_ride_hail_trip', response)

#     @route('/driver_arrived_for_dropoff', methods=['PATCH'])
#     def driver_arrived_for_dropoff(self, **lookup): #run_id, _id):
#         """End an active Driver-Trip
#         ---
#         patch:
#         description: Update trip and set state to Complete with provision for force_quit.
#         if force_quit is false, The endpoint validates State Transition
#         security:
#             - ApiKeyAuth: []
#         responses:
#             200:
#             content:
#                 application/json:
#                 schema: PetSchema

#         """
#         if config.IF_MATCH:
#             lookup[config.ETAG] = request.headers['If-Match']
#         # print(lookup)

#         payload = request.json

#         payload['transition'] =  RidehailPassengerTripStateMachine.driver_arrived_for_dropoff.identifier

#         response = patch_internal('passenger_ride_hail_trip',
#                                     skip_validation=True, # Done to ensure sim_clock is updatable
#                                     payload=payload,
#                                     **lookup
#                                 )
#         return send_response('passenger_ride_hail_trip', response)

#     @route('/driver_waiting_for_dropoff', methods=['PATCH'])
#     def driver_waiting_for_dropoff(self, **lookup): #run_id, _id):
#         """End an active Driver-Trip
#         ---
#         patch:
#         description: Update trip and set state to Complete with provision for force_quit.
#         if force_quit is false, The endpoint validates State Transition
#         security:
#             - ApiKeyAuth: []
#         responses:
#             200:
#             content:
#                 application/json:
#                 schema: PetSchema

#         """
#         if config.IF_MATCH:
#             lookup[config.ETAG] = request.headers['If-Match']
#         # print(lookup)

#         payload = request.json

#         payload['transition'] =  RidehailPassengerTripStateMachine.driver_waiting_for_dropoff.identifier

#         response = patch_internal('passenger_ride_hail_trip',
#                                     skip_validation=True, # Done to ensure sim_clock is updatable
#                                     payload=payload,
#                                     **lookup
#                                 )
#         return send_response('passenger_ride_hail_trip', response)

#     @route('/end_trip', methods=['PATCH'])
#     def end_trip(self, **lookup): #run_id, _id):
#         """End an active passenger-Trip
#         ---
#         patch:
#         description: Update trip and set state to Complete with provision for force_quit.
#         if force_quit is false, The endpoint validates State Transition
#         security:
#             - ApiKeyAuth: []
#         responses:
#             200:
#             content:
#                 application/json:
#                 schema: PetSchema

#         """
#         if config.IF_MATCH:
#             lookup[config.ETAG] = request.headers['If-Match']
#         # print(lookup)

#         payload = request.json

#         payload['transition'] =  RidehailPassengerTripStateMachine.end_trip.identifier

#         response = patch_internal('passenger_ride_hail_trip',
#                                     skip_validation=True, # Done to ensure sim_clock is updatable
#                                     payload=payload,
#                                     **lookup
#                                 )
#         return send_response('passenger_ride_hail_trip', response)

#     @route('/force_quit', methods=['PATCH'])
#     def force_quit(self, **lookup): #run_id, _id):
#         """End an active passenger-Trip
#         ---
#         patch:
#         description: Update trip and set state to Complete with provision for force_quit.
#         if force_quit is false, The endpoint validates State Transition
#         security:
#             - ApiKeyAuth: []
#         responses:
#             200:
#             content:
#                 application/json:
#                 schema: PetSchema

#         """
#         if config.IF_MATCH:
#             lookup[config.ETAG] = request.headers['If-Match']
#         # print(lookup)

#         payload = request.json

#         try:
#             payload['transition'] =  RidehailPassengerTripStateMachine.force_quit.identifier
#             payload['force_quit'] =  True
#         except: pass

#         payload['is_active'] =  False

#         response = patch_internal('passenger_ride_hail_trip',
#                                     skip_validation=True, # Done to ensure sim_clock is updatable
#                                     payload=payload,
#                                     **lookup
#                                 )

#         return send_response('passenger_ride_hail_trip', response)

# class PassengerRideHailTripCollectionView(FlaskView):
#     ''' '''
#     route_prefix = '/<run_id>/passenger/ride_hail/trip'
#     route_base = '/'
#     decorators = [requires_auth('passenger_ride_hail_trip')]


#     @route('/state/<state>', methods=['GET'])
#     def list_by_state(self, **lookup): #run_id, _id):
#         """The first line is the summary!

#         All the rest goes in the description.

#         """
#         db = app.data.driver.db
#         projection = json.loads(request.args.get('projection'))
#         # print(projection)

#         cursor = db['passenger_ride_hail_trip'].find(
#             lookup,
#             projection=projection
#         )

#         # return jsonify(data), 200
#         return send_response('passenger_ride_hail_trip', (list(cursor), None, None, 200, []))

