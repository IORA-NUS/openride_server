from api.config import simulation_domains
from api.utils import persona_schema, statemachine_schema


class Facility:
    """
    Container-logistics facility resource (gate queue lifecycle).

    Counterpart to `apps.container_logistics.facility.FacilityManager` and
    `GateStateMachine`.
    """

    schema = {
        "run_id": {"type": "string", "required": True},
        "profile": {"type": "dict", "required": True, "allow_unknown": True, "default": {}},
        "persona": {"type": "dict", "schema": persona_schema, "required": True, "allow_unknown": True},
        "num_gates": {"type": "integer", "required": False},
        "pickup_service_time": {"type": "integer", "required": False},
        "dropoff_service_time": {"type": "integer", "required": False},
        "statemachine": {"type": "dict", "schema": statemachine_schema, "required": True},
        "state": {"type": "string", "required": True},
        "transition": {"type": "string", "required": False},
        "feasible_transitions": {"type": "list", "required": False, "default": [], "readonly": True},
        "sim_clock": {"type": "datetime", "required": False},
    }

    model = {
        "datasource": {"source": "container_logistics_facility"},
        "url": f"{simulation_domains['container_logistics']}/<regex(\"[a-zA-Z0-9_-]*\"):run_id>/facility",
        "schema": schema,
        "mongo_indexes": {
            "run_id_persona_role": ([("run_id", 1), ("persona.role", 1)], {"background": True}),
        },
        "resource_methods": ["GET", "POST"],
        "item_methods": ["GET", "PATCH"],
    }
