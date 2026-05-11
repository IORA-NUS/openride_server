from api.config import simulation_domains
from api.utils import persona_schema, statemachine_schema


class Order:
    """
    Container-logistics order resource (job request lifecycle).

    This is the counterpart to `apps.container_logistics.order.OrderManager` and
    `apps.container_logistics.statemachine.OrderStateMachine`.
    """

    schema = {
        "run_id": {"type": "string", "required": True},
        "profile": {"type": "dict", "required": False, "allow_unknown": True, "default": {}},
        "persona": {"type": "dict", "schema": persona_schema, "required": True, "allow_unknown": True},
        "truck": {"type": "objectid", "required": False},
        "pickup_loc": {"type": "point", "required": False},
        "dropoff_loc": {"type": "point", "required": False},
        "stats": {"type": "dict", "required": False, "allow_unknown": True},
        "meta": {"type": "dict", "required": False, "allow_unknown": True},
        "state": {"type": "string", "required": True},
        "transition": {"type": "string", "required": False},
        "feasible_transitions": {"type": "list", "required": False, "default": [], "readonly": True},
        "statemachine": {"type": "dict", "schema": statemachine_schema, "required": True},
        "sim_clock": {"type": "datetime", "required": False},
    }

    model = {
        "datasource": {"source": "container_logistics_order"},
        "url": f"{simulation_domains['container_logistics']}/<regex(\"[a-zA-Z0-9_-]*\"):run_id>/order",
        "schema": schema,
        "mongo_indexes": {
            "run_id_state": ([("run_id", 1), ("state", 1)], {"background": True}),
        },
        "resource_methods": ["GET", "POST"],
        "item_methods": ["GET", "PATCH"],
    }

