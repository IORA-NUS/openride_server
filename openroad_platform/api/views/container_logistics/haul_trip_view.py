from flask import current_app as app
from flask import abort, Response, request

from flask_classful import FlaskView, route
from eve.auth import requires_auth
from eve.utils import config
from eve.render import send_response
from eve.methods.get import get_internal
from eve.methods.patch import patch_internal

from api.config import simulation_domains
from api.utils import patch_timestamps
from api.controllers.container_logistics import HaulTripController


class HaulTripView:
    @classmethod
    def on_insert(cls, documents):
        if len(documents) > 1:
            abort(Response("Insert accepts only a single item", status=403))
        try:
            for document in documents:
                patch_timestamps(document)
                statemachine = document.get("statemachine")
                if statemachine:
                    name = statemachine.get("name")
                    domain = statemachine.get("domain")
                    if name and domain:
                        db = app.data.driver.db
                        sm = db["statemachine"].find_one({"name": name, "domain": domain})
                        if sm:
                            document["statemachine"]["id"] = sm["_id"]
                HaulTripController.validate(document)
        except Exception as e:
            app.logger.error(f"Error inserting haul trip: {e}")
            abort(Response(str(e), status=403))

    @classmethod
    def on_update(cls, updates, document):
        try:
            patch_timestamps(updates, update_only=True)
            HaulTripController.validate(document, updates)
        except Exception as e:
            abort(Response(str(e), status=403))


class HaulTripWorkflowView(FlaskView):
    route_prefix = f"{simulation_domains['container_logistics']}/<run_id>/truck/trip"
    route_base = "/"
    decorators = [requires_auth("container_logistics_haul_trip")]

    def before_patch(self, name, *args, **kwargs):
        if config.IF_MATCH:
            kwargs[config.ETAG] = request.headers["If-Match"]

        # Validate existence (and allow validator to run) for PATCH calls.
        response = get_internal("container_logistics_haul_trip", **kwargs)
        _ = response[0]["_items"][0]

        # Patch timestamps based on sim_clock if present.
        patch_timestamps(request.json, update_only=True)

    @route("/<_id>/<transition>", methods=["PATCH"])
    def patch_transition(self, **lookup):
        if config.IF_MATCH:
            lookup[config.ETAG] = request.headers["If-Match"]

        payload = request.json
        payload["transition"] = lookup.pop("transition")
        response = patch_internal(
            "container_logistics_haul_trip",
            skip_validation=True,
            payload=payload,
            **lookup,
        )
        return send_response("container_logistics_haul_trip", response)

