from api.config import simulation_domains
from api.utils import persona_schema, statemachine_schema


class HaulTrip:
    """
    Container-logistics haul trip (job execution lifecycle).

    Minimal schema needed for TruckTripManager in openride_apps.
    We allow unknown fields in stats/meta/routes to keep the first pass flexible.
    """

    schema = {
        "run_id": {"type": "string", "required": True},
        "truck": {"type": "objectid", "required": True},
        "order": {"type": "string", "required": False},
        "persona": {"type": "dict", "schema": persona_schema, "required": True, "allow_unknown": True},
        "meta": {"type": "dict", "required": False, "allow_unknown": True},
        "current_loc": {"type": "point", "required": True},
        "pickup_loc": {"type": "point", "required": False},
        "dropoff_loc": {"type": "point", "required": False},
        "gate_index": {"type": "integer", "required": False},
        "routes": {"type": "dict", "required": False, "allow_unknown": True},
        "stats": {"type": "dict", "required": False, "allow_unknown": True},
        "state": {"type": "string", "required": True},
        "transition": {"type": "string", "required": False},
        "feasible_transitions": {"type": "list", "required": False, "default": [], "readonly": True},
        "statemachine": {"type": "dict", "schema": statemachine_schema, "required": True},
        "sim_clock": {"type": "datetime", "required": False},
    }

    model = {
        "datasource": {"source": "container_logistics_haul_trip"},
        # Trip endpoint matches openride_apps TripManagerBase role path:
        #   /<domain>/<run_id>/truck/trip
        "url": f"{simulation_domains['container_logistics']}/<regex(\"[a-zA-Z0-9_-]*\"):run_id>/truck/trip",
        "schema": schema,
        "mongo_indexes": {
            "run_id_truck_state": ([("run_id", 1), ("truck", 1), ("state", 1)], {"background": True}),
        },
        "resource_methods": ["GET", "POST"],
        "item_methods": ["GET", "PATCH"],
    }

