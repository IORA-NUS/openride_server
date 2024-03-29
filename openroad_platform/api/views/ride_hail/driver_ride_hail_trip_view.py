import json
import traceback

from flask import current_app as app
from flask import abort, Response, request, jsonify, Blueprint, make_response

from flask_classful import FlaskView, route
from eve.auth import requires_auth
from eve.utils import config, parse_request
from eve.render import send_response


# from flask_jwt_extended import get_jwt, jwt_required, verify_jwt_in_request
from bson.objectid import ObjectId

from api.utils import Status
from api.controllers import DriverRideHailTripController

from eve.methods.get import get_internal
from eve.auth import auth_field_and_value

from eve.methods.patch import patch_internal
from api.state_machine import RidehailDriverTripStateMachine


class DriverRideHailTripView:
    ''' '''

    @classmethod
    def on_insert(cls, documents):
        ''' '''
        # print(documents)
        if len(documents) > 1:
            abort(Response("Insert accepts only a single item", status=403))

        document = documents[0]
        try:
            DriverRideHailTripController.validate(document)
            # if document.get('passenger') is not None:
            #     document['state'] = RidehailDriverTripStateMachine.driver_received_trip.identifier

            if document.get('sim_clock') is not None:
                document['_created'] = document['sim_clock']
                document['_updated'] = document['sim_clock']
        except Exception as e:
            abort(Response(str(e), status=403))


    @classmethod
    def on_update(cls, updates, document):
        ''' '''
        try:
            DriverRideHailTripController.validate(document, updates)
            if updates.get('sim_clock') is not None:
                updates['_updated'] = updates['sim_clock']
        except Exception as e:
            abort(Response(str(e), status=403))


    @classmethod
    def on_inserted(cls, documents):
        ''' '''
        document = documents[0]
        try:
            DriverRideHailTripController.add_waypoint(document)
        except Exception as e:
            abort(Response(str(e), status=403))

    @classmethod
    def on_updated(cls, updates, document):
        ''' '''
        try:
            DriverRideHailTripController.add_waypoint(document, updates)
        except Exception as e:
            abort(Response(str(e), status=403))




class DriverRideHailTripWorkflowView(FlaskView):
    ''' '''
    route_prefix = '/<run_id>/driver/ride_hail/trip'
    route_base = '/'
    decorators = [requires_auth('driver_ride_hail_trip')]


    def before_patch(self, name, *args, **kwargs):
        ''' '''
        if config.IF_MATCH:
            kwargs[config.ETAG] = request.headers['If-Match']

        if name in []:  # NOTE Include validation for all methods that use POST / PUT
            document = request.json
            DriverRideHailTripController.validate(document)
        else: # NOTE Include validation for all methods that use PATCH
            response = get_internal('driver_ride_hail_trip', **kwargs)
            document = response[0]['_items'][0] # Raises exception if document is not found.
            updates = request.json
            DriverRideHailTripController.validate(document, updates)

        if request.json.get('sim_clock') is not None:
            if name in []:
                request.json['_created'] = request.json['sim_clock']

            request.json['_updated'] = request.json['sim_clock']

    @route('/<_id>/<transition>', methods=['PATCH'])
    def patch_transition(self, **lookup): #run_id, _id):
        """The first line is the summary!

        All the rest goes in the description.

        """
        if config.IF_MATCH:
            lookup[config.ETAG] = request.headers['If-Match']

        payload = request.json
        payload['transition'] = lookup.pop('transition')

        response = patch_internal('driver_ride_hail_trip',
                                    skip_validation=True, # Done to ensure sim_clock is updatable
                                    payload=payload,
                                    **lookup
                                )
        return send_response('driver_ride_hail_trip', response)

    @route('/state/<state>', methods=['GET'])
    def list_by_state(self, **lookup): #run_id, _id):
        """The first line is the summary!

        All the rest goes in the description.

        """
        db = app.data.driver.db
        projection = json.loads(request.args.get('projection'))
        # print(projection)

        cursor = db['driver_ride_hail_trip'].find(
            lookup,
            projection=projection
        )

        # return jsonify(data), 200
        return send_response('driver_ride_hail_trip', (list(cursor), None, None, 200, []))

# class DriverRideHailTripWorkflowView(FlaskView):
#     ''' '''
#     route_prefix = '/<run_id>/driver/ride_hail/trip/<_id>'
#     route_base = '/'
#     decorators = [requires_auth('driver_ride_hail_trip')]


#     def before_request(self, name, *args, **kwargs):
#         ''' '''
#         # db = app.data.driver.db
#         if config.IF_MATCH:
#             kwargs[config.ETAG] = request.headers['If-Match']

#         # verify_jwt_in_request()
#         # id_payload = get_jwt()[app.config["JWT_IDENTITY_CLAIM"]]
#         # kwargs[app.config["AUTH_FIELD"]] = id_payload['_id']
#         # print(kwargs)

#         # print(f"{name=}, {args=}, {kwargs=}")

#         if name in []:  # NOTE Include validation for all methods that use POST / PUT
#             document = request.json
#             DriverRideHailTripController.validate(document)
#         else: # NOTE Include validation for all methods that use PATCH
#             response = get_internal('driver_ride_hail_trip', **kwargs)
#             # print(response[0])
#             document = response[0]['_items'][0] # Raises exception if document is not found.
#             updates = request.json
#             DriverRideHailTripController.validate(document, updates)

#         # print(f"{request.json.get('sim_clock')=}")
#         if request.json.get('sim_clock') is not None:
#             if name in []:
#                 request.json['_created'] = request.json['sim_clock']

#             request.json['_updated'] = request.json['sim_clock']

#     @route('/look_for_job', methods=['PATCH'])
#     def look_for_job(self, **lookup): #run_id, _id):
#         """The first line is the summary!

#         All the rest goes in the description.

#         """
#         if config.IF_MATCH:
#             lookup[config.ETAG] = request.headers['If-Match']
#         # print(lookup)

#         payload = request.json
#         payload['transition'] =  RidehailDriverTripStateMachine.look_for_job.identifier

#         response = patch_internal('driver_ride_hail_trip',
#                                     skip_validation=True, # Done to ensure sim_clock is updatable
#                                     payload=payload,
#                                     **lookup
#                                 )
#         return send_response('driver_ride_hail_trip', response)

#     @route('/recieve', methods=['PATCH'])
#     def recieve(self, **lookup): #run_id, _id):
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

#         payload['transition'] =  RidehailDriverTripStateMachine.recieve.identifier

#         response = patch_internal('driver_ride_hail_trip',
#                                     skip_validation=True, # Done to ensure sim_clock is updatable
#                                     payload=payload,
#                                     **lookup
#                                 )
#         return send_response('driver_ride_hail_trip', response)

#     @route('/confirm', methods=['PATCH'])
#     def confirm(self, **lookup): #run_id, _id):
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

#         payload['transition'] =  RidehailDriverTripStateMachine.confirm.identifier

#         response = patch_internal('driver_ride_hail_trip',
#                                     skip_validation=True, # Done to ensure sim_clock is updatable
#                                     payload=payload,
#                                     **lookup
#                                 )
#         return send_response('driver_ride_hail_trip', response)

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

#         payload['transition'] =  RidehailDriverTripStateMachine.reject.identifier

#         response = patch_internal('driver_ride_hail_trip',
#                                     skip_validation=True, # Done to ensure sim_clock is updatable
#                                     payload=payload,
#                                     **lookup
#                                 )
#         return send_response('driver_ride_hail_trip', response)

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

#         payload['transition'] =  RidehailDriverTripStateMachine.cancel.identifier

#         response = patch_internal('driver_ride_hail_trip',
#                                     skip_validation=True, # Done to ensure sim_clock is updatable
#                                     payload=payload,
#                                     **lookup
#                                 )
#         return send_response('driver_ride_hail_trip', response)

#     @route('/passenger_confirmed_trip', methods=['PATCH'])
#     def passenger_confirmed_trip(self, **lookup): #run_id, _id):
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

#         payload['transition'] =  RidehailDriverTripStateMachine.passenger_confirmed_trip.identifier

#         response = patch_internal('driver_ride_hail_trip',
#                                     skip_validation=True, # Done to ensure sim_clock is updatable
#                                     payload=payload,
#                                     **lookup
#                                 )
#         return send_response('driver_ride_hail_trip', response)

#     @route('/wait_to_pickup', methods=['PATCH'])
#     def wait_to_pickup(self, **lookup): #run_id, _id):
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

#         payload['transition'] =  RidehailDriverTripStateMachine.wait_to_pickup.identifier

#         response = patch_internal('driver_ride_hail_trip',
#                                     skip_validation=True, # Done to ensure sim_clock is updatable
#                                     payload=payload,
#                                     **lookup
#                                 )
#         return send_response('driver_ride_hail_trip', response)

#     @route('/passenger_acknowledge_pickup', methods=['PATCH'])
#     def passenger_acknowledge_pickup(self, **lookup): #run_id, _id):
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

#         payload['transition'] =  RidehailDriverTripStateMachine.passenger_acknowledge_pickup.identifier

#         response = patch_internal('driver_ride_hail_trip',
#                                     skip_validation=True, # Done to ensure sim_clock is updatable
#                                     payload=payload,
#                                     **lookup
#                                 )
#         return send_response('driver_ride_hail_trip', response)

#     @route('/move_to_dropoff', methods=['PATCH'])
#     def move_to_dropoff(self, **lookup): #run_id, _id):
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

#         payload['transition'] =  RidehailDriverTripStateMachine.move_to_dropoff.identifier

#         response = patch_internal('driver_ride_hail_trip',
#                                     skip_validation=True, # Done to ensure sim_clock is updatable
#                                     payload=payload,
#                                     **lookup
#                                 )
#         return send_response('driver_ride_hail_trip', response)

#     @route('/wait_to_dropoff', methods=['PATCH'])
#     def wait_to_dropoff(self, **lookup): #run_id, _id):
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

#         payload['transition'] =  RidehailDriverTripStateMachine.wait_to_dropoff.identifier

#         response = patch_internal('driver_ride_hail_trip',
#                                     skip_validation=True, # Done to ensure sim_clock is updatable
#                                     payload=payload,
#                                     **lookup
#                                 )
#         return send_response('driver_ride_hail_trip', response)

#     @route('/passenger_acknowledge_dropoff', methods=['PATCH'])
#     def passenger_acknowledge_dropoff(self, **lookup): #run_id, _id):
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

#         payload['transition'] =  RidehailDriverTripStateMachine.passenger_acknowledge_dropoff.identifier

#         response = patch_internal('driver_ride_hail_trip',
#                                     skip_validation=True, # Done to ensure sim_clock is updatable
#                                     payload=payload,
#                                     **lookup
#                                 )
#         return send_response('driver_ride_hail_trip', response)

#     @route('/end_trip', methods=['PATCH'])
#     def end_trip(self, **lookup): #run_id, _id):
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

#         payload['transition'] =  RidehailDriverTripStateMachine.end_trip.identifier

#         response = patch_internal('driver_ride_hail_trip',
#                                     skip_validation=True, # Done to ensure sim_clock is updatable
#                                     payload=payload,
#                                     **lookup
#                                 )
#         return send_response('driver_ride_hail_trip', response)

#     @route('/force_quit', methods=['PATCH'])
#     def force_quit(self, **lookup): #run_id, _id):
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

#         payload['transition'] =  RidehailDriverTripStateMachine.force_quit.identifier
#         payload['is_active'] =  False
#         payload['force_quit'] =  True

#         response = patch_internal('driver_ride_hail_trip',
#                                     skip_validation=True, # Done to ensure sim_clock is updatable
#                                     payload=payload,
#                                     **lookup
#                                 )

#         return send_response('driver_ride_hail_trip', response)



# class DriverRideHailTripCollectionView(FlaskView):
#     ''' '''
#     route_prefix = '/<run_id>/driver/ride_hail/trip'
#     route_base = '/'
#     decorators = [requires_auth('driver_ride_hail_trip')]


#     @route('/state/<state>', methods=['GET'])
#     def list_by_state(self, **lookup): #run_id, _id):
#         """The first line is the summary!

#         All the rest goes in the description.

#         """
#         db = app.data.driver.db
#         projection = json.loads(request.args.get('projection'))
#         # print(projection)

#         cursor = db['driver_ride_hail_trip'].find(
#             lookup,
#             projection=projection
#         )

#         # return jsonify(data), 200
#         return send_response('driver_ride_hail_trip', (list(cursor), None, None, 200, []))

