from flask import current_app as app
from flask import abort, Response

from api.utils import patch_timestamps
from api.controllers.container_logistics import TruckController


class TruckView:
    @classmethod
    def on_insert(cls, documents):
        try:
            for document in documents:
                patch_timestamps(document)
                # Bind statemachine id when provided by name+domain
                statemachine = document.get("statemachine")
                if statemachine:
                    name = statemachine.get("name")
                    domain = statemachine.get("domain")
                    if name and domain:
                        db = app.data.driver.db
                        sm = db["statemachine"].find_one({"name": name, "domain": domain})
                        if sm:
                            document["statemachine"]["id"] = sm["_id"]
                TruckController.validate(document)
        except Exception as e:
            app.logger.error(f"Error inserting truck: {e}")
            abort(Response(str(e), status=403))

    @classmethod
    def on_update(cls, updates, document):
        try:
            patch_timestamps(updates, update_only=True)
            TruckController.validate(document, updates)
        except Exception as e:
            app.logger.error(f"Error updating truck: {e}")
            abort(Response(str(e), status=403))

