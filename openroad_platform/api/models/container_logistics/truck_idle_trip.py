from api.config import simulation_domains
from api.utils import persona_schema


class TruckIdleTrip:
    """
    Optional persisted idle trip stream for trucks (viz/analytics).
    Does not participate in haul-trip assignment gating.
    """

    schema = {
        "run_id": {"type": "string", "required": True},
        "persona": {"type": "dict", "schema": persona_schema, "required": True, "allow_unknown": True},
        "kind": {"type": "string", "required": True, "allowed": ["idle"]},
        "state": {"type": "string", "required": True},
        "start_loc": {"type": "point", "required": False},
        "end_loc": {"type": "point", "required": False},
        "current_loc": {"type": "point", "required": False},
        "next_dest_loc": {"type": "point", "required": False},
        "routes": {"type": "dict", "required": False, "allow_unknown": True},
        "start_sim_clock": {"type": "datetime", "required": False},
        "end_sim_clock": {"type": "datetime", "required": False},
        "sim_clock": {"type": "datetime", "required": False},
    }

    model = {
        "datasource": {"source": "container_logistics_truck_idle_trip"},
        "url": f"{simulation_domains['container_logistics']}/<regex(\"[a-zA-Z0-9_-]*\"):run_id>/truck_idle_trip",
        "schema": schema,
        "resource_methods": ["GET", "POST"],
        "item_methods": ["GET", "PATCH"],
    }

