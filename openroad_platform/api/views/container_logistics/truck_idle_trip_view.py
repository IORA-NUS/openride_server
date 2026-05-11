from flask import current_app as app
from flask import abort, Response

from api.utils import patch_timestamps


class TruckIdleTripView:
    @classmethod
    def on_insert(cls, documents):
        try:
            for document in documents:
                patch_timestamps(document)
        except Exception as e:
            app.logger.error(f"Error inserting truck idle trip: {e}")
            abort(Response(str(e), status=403))

    @classmethod
    def on_update(cls, updates, document):
        try:
            patch_timestamps(updates, update_only=True)
        except Exception as e:
            app.logger.error(f"Error updating truck idle trip: {e}")
            abort(Response(str(e), status=403))

