import json
import traceback

from flask import current_app as app
from flask import abort, Response, request, jsonify, Blueprint, make_response

from flask_classful import FlaskView, route
from eve.auth import requires_auth
from eve.utils import config
from eve.render import send_response


# from flask_jwt_extended import get_jwt, jwt_required
from bson.objectid import ObjectId

from api.utils import Status
from api.controllers import DriverTripController

from eve.methods.get import get_internal
from eve.auth import auth_field_and_value

from eve.methods.patch import patch_internal
from api.lib import RidehailDriverTripStateMachine


class DriverTripView:
    ''' '''

    @classmethod
    def on_insert(cls, documents):
        ''' '''
        # print(documents)
        if len(documents) > 1:
            abort(Response("Insert accepts only a single item", status=403))

        document = documents[0]
        try:
            DriverTripController.validate(document)
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
            DriverTripController.validate(document, updates)
            if updates.get('sim_clock') is not None:
                updates['_updated'] = updates['sim_clock']
        except Exception as e:
            abort(Response(str(e), status=403))


    @classmethod
    def on_inserted(cls, documents):
        ''' '''
        document = documents[0]
        try:
            DriverTripController.add_waypoint(document)
        except Exception as e:
            abort(Response(str(e), status=403))

    @classmethod
    def on_updated(cls, updates, document):
        ''' '''
        try:
            DriverTripController.add_waypoint(document, updates)
        except Exception as e:
            abort(Response(str(e), status=403))


class DriverTripWorkflowView(FlaskView):
    ''' '''
    route_prefix = '/<run_id>/driver/trip/<_id>'
    route_base = '/'
    decorators = [requires_auth('driver_trip')]


    def before_request(self, name, *args, **kwargs):
        ''' '''
        # db = app.data.driver.db
        if config.IF_MATCH:
            kwargs[config.ETAG] = request.headers['If-Match']

        # print(name, args, kwargs)

        if name in []:  # NOTE Include validation for all methods that use POST / PUT
            document = request.json
            DriverTripController.validate(document)
        else: # NOTE Include validation for all methods that use PATCH
            response = get_internal('driver_trip', **kwargs)
            # print(response[0])
            document = response[0]['_items'][0] # Raises exception if document is not found.
            updates = request.json
            DriverTripController.validate(document, updates)


        if request.json.get('sim_clock') is not None:
            if name in []:
                request.json['_created'] = request.json['sim_clock']

            request.json['_updated'] = request.json['sim_clock']

    @route('/look_for_job', methods=['PATCH'])
    def look_for_job(self, **lookup): #run_id, _id):
        """The first line is the summary!

        All the rest goes in the description.

        """
        if config.IF_MATCH:
            lookup[config.ETAG] = request.headers['If-Match']
        # print(lookup)

        payload = request.json
        payload['transition'] =  RidehailDriverTripStateMachine.look_for_job.identifier

        response = patch_internal('driver_trip',
                                    skip_validation=True, # Done to ensure sim_clock is updatable
                                    payload=payload,
                                    **lookup
                                )
        return send_response('driver_trip', response)

    @route('/recieve', methods=['PATCH'])
    def recieve(self, **lookup): #run_id, _id):
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
        # print(lookup)

        payload = request.json

        payload['transition'] =  RidehailDriverTripStateMachine.recieve.identifier

        response = patch_internal('driver_trip',
                                    skip_validation=True, # Done to ensure sim_clock is updatable
                                    payload=payload,
                                    **lookup
                                )
        return send_response('driver_trip', response)

    @route('/confirm', methods=['PATCH'])
    def confirm(self, **lookup): #run_id, _id):
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
        # print(lookup)

        payload = request.json

        payload['transition'] =  RidehailDriverTripStateMachine.confirm.identifier

        response = patch_internal('driver_trip',
                                    skip_validation=True, # Done to ensure sim_clock is updatable
                                    payload=payload,
                                    **lookup
                                )
        return send_response('driver_trip', response)

    @route('/reject', methods=['PATCH'])
    def reject(self, **lookup): #run_id, _id):
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
        # print(lookup)

        payload = request.json

        payload['transition'] =  RidehailDriverTripStateMachine.reject.identifier

        response = patch_internal('driver_trip',
                                    skip_validation=True, # Done to ensure sim_clock is updatable
                                    payload=payload,
                                    **lookup
                                )
        return send_response('driver_trip', response)

    @route('/cancel', methods=['PATCH'])
    def cancel(self, **lookup): #run_id, _id):
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
        # print(lookup)

        payload = request.json

        payload['transition'] =  RidehailDriverTripStateMachine.cancel.identifier

        response = patch_internal('driver_trip',
                                    skip_validation=True, # Done to ensure sim_clock is updatable
                                    payload=payload,
                                    **lookup
                                )
        return send_response('driver_trip', response)

    @route('/passenger_confirmed_trip', methods=['PATCH'])
    def passenger_confirmed_trip(self, **lookup): #run_id, _id):
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
        # print(lookup)

        payload = request.json

        payload['transition'] =  RidehailDriverTripStateMachine.passenger_confirmed_trip.identifier

        response = patch_internal('driver_trip',
                                    skip_validation=True, # Done to ensure sim_clock is updatable
                                    payload=payload,
                                    **lookup
                                )
        return send_response('driver_trip', response)

    @route('/wait_to_pickup', methods=['PATCH'])
    def wait_to_pickup(self, **lookup): #run_id, _id):
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
        # print(lookup)

        payload = request.json

        payload['transition'] =  RidehailDriverTripStateMachine.wait_to_pickup.identifier

        response = patch_internal('driver_trip',
                                    skip_validation=True, # Done to ensure sim_clock is updatable
                                    payload=payload,
                                    **lookup
                                )
        return send_response('driver_trip', response)

    @route('/passenger_acknowledge_pickup', methods=['PATCH'])
    def passenger_acknowledge_pickup(self, **lookup): #run_id, _id):
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
        # print(lookup)

        payload = request.json

        payload['transition'] =  RidehailDriverTripStateMachine.passenger_acknowledge_pickup.identifier

        response = patch_internal('driver_trip',
                                    skip_validation=True, # Done to ensure sim_clock is updatable
                                    payload=payload,
                                    **lookup
                                )
        return send_response('driver_trip', response)

    @route('/move_to_dropoff', methods=['PATCH'])
    def move_to_dropoff(self, **lookup): #run_id, _id):
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
        # print(lookup)

        payload = request.json

        payload['transition'] =  RidehailDriverTripStateMachine.move_to_dropoff.identifier

        response = patch_internal('driver_trip',
                                    skip_validation=True, # Done to ensure sim_clock is updatable
                                    payload=payload,
                                    **lookup
                                )
        return send_response('driver_trip', response)

    @route('/wait_to_dropoff', methods=['PATCH'])
    def wait_to_dropoff(self, **lookup): #run_id, _id):
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
        # print(lookup)

        payload = request.json

        payload['transition'] =  RidehailDriverTripStateMachine.wait_to_dropoff.identifier

        response = patch_internal('driver_trip',
                                    skip_validation=True, # Done to ensure sim_clock is updatable
                                    payload=payload,
                                    **lookup
                                )
        return send_response('driver_trip', response)

    @route('/passenger_acknowledge_dropoff', methods=['PATCH'])
    def passenger_acknowledge_dropoff(self, **lookup): #run_id, _id):
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
        # print(lookup)

        payload = request.json

        payload['transition'] =  RidehailDriverTripStateMachine.passenger_acknowledge_dropoff.identifier

        response = patch_internal('driver_trip',
                                    skip_validation=True, # Done to ensure sim_clock is updatable
                                    payload=payload,
                                    **lookup
                                )
        return send_response('driver_trip', response)

    @route('/end_trip', methods=['PATCH'])
    def end_trip(self, **lookup): #run_id, _id):
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
        # print(lookup)

        payload = request.json

        payload['transition'] =  RidehailDriverTripStateMachine.end_trip.identifier

        response = patch_internal('driver_trip',
                                    skip_validation=True, # Done to ensure sim_clock is updatable
                                    payload=payload,
                                    **lookup
                                )
        return send_response('driver_trip', response)

    @route('/force_quit', methods=['PATCH'])
    def force_quit(self, **lookup): #run_id, _id):
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
        # print(lookup)

        payload = request.json

        payload['is_active'] =  False
        payload['force_quit'] =  True

        response = patch_internal('driver_trip',
                                    skip_validation=True, # Done to ensure sim_clock is updatable
                                    payload=payload,
                                    **lookup
                                )

        return send_response('driver_trip', response)
