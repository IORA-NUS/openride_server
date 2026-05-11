from api.config import simulation_domains
from api.utils import persona_schema, statemachine_schema


class Truck:
    """
    Container-logistics truck resource (availability lifecycle).

    Minimal schema needed for TruckManager in openride_apps:
    - profile/persona metadata
    - statemachine + state
    - sim_clock for timestamp patching
    """

    schema = {
        "run_id": {"type": "string", "required": True},
        "profile": {"type": "dict", "required": True, "allow_unknown": True, "default": {}},
        "persona": {"type": "dict", "schema": persona_schema, "required": True, "allow_unknown": True},
        "statemachine": {"type": "dict", "schema": statemachine_schema, "required": True},
        "state": {"type": "string", "required": True},
        "transition": {"type": "string", "required": False},
        "sim_clock": {"type": "datetime", "required": False},
    }

    model = {
        "datasource": {"source": "container_logistics_truck"},
        "url": f"{simulation_domains['container_logistics']}/<regex(\"[a-zA-Z0-9_-]*\"):run_id>/truck",
        "schema": schema,
        "mongo_indexes": {
            "run_id_persona_role": ([("run_id", 1), ("persona.role", 1)], {"background": True}),
        },
        "resource_methods": ["GET", "POST"],
        "item_methods": ["GET", "PATCH"],
    }

