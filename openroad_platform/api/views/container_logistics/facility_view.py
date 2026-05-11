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
from api.controllers.container_logistics import FacilityController


class FacilityView:
    @classmethod
    def on_insert(cls, documents):
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
                FacilityController.validate(document)
        except Exception as e:
            app.logger.error(f"Error inserting facility: {e}")
            abort(Response(str(e), status=403))

    @classmethod
    def on_update(cls, updates, document):
        try:
            patch_timestamps(updates, update_only=True)
            FacilityController.validate(document, updates)
        except Exception as e:
            app.logger.error(f"Error updating facility: {e}")
            abort(Response(str(e), status=403))


class FacilityWorkflowView(FlaskView):
    route_prefix = f"{simulation_domains['container_logistics']}/<run_id>/facility"
    route_base = "/"
    decorators = [requires_auth("container_logistics_facility")]

    def before_patch(self, name, *args, **kwargs):
        if config.IF_MATCH:
            kwargs[config.ETAG] = request.headers["If-Match"]

        response = get_internal("container_logistics_facility", **kwargs)
        _ = response[0]["_items"][0]

        patch_timestamps(request.json, update_only=True)

    @route("/<_id>/<transition>", methods=["PATCH"])
    def patch_transition(self, **lookup):
        if config.IF_MATCH:
            lookup[config.ETAG] = request.headers["If-Match"]

        payload = request.json
        payload["transition"] = lookup.pop("transition")
        response = patch_internal(
            "container_logistics_facility",
            skip_validation=True,
            payload=payload,
            **lookup,
        )
        return send_response("container_logistics_facility", response)
