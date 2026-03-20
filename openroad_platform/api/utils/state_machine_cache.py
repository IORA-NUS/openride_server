# state_machine_cache.py
"""
Worker-level cache for state machine classes with robust definition checking.
"""

from threading import Lock
from typing import Any, Dict, Tuple
from orsim.utils import StateMachineSerializer


 # Example cache structure: {definition_id: (class_obj, version)}
_cache: Dict[str, Tuple[Any, str]] = {}
_cache_lock = Lock()


def get_state_machine(definition_id: str, get_definition_func) -> Any:
    """
    Retrieve state machine class for a definition ID.
    Checks cache, verifies version, reloads if needed.
    Args:
        definition_id: Unique identifier for the state machine definition.
        get_definition_func: Callable returning (definition, version) from DB.
    Returns:
        State machine class
    """
    with _cache_lock:
        cached = _cache.get(definition_id)
        definition, version = get_definition_func(definition_id)
        if cached and cached[1] == version:
            return cached[0]
        # Reconstruct class from definition
        class_obj = construct_state_machine_class(definition)
        _cache[definition_id] = (class_obj, version)
        return class_obj


def invalidate_state_machine(definition_id: str):
    """
    Remove a cached state machine class for a definition ID.
    Call after definition update/create.
    """
    with _cache_lock:
        _cache.pop(definition_id, None)


def construct_state_machine_class(definition: dict) -> Any:
    """
    Construct a state machine class from a definition dict using StateMachineSerializer.
    Returns:
        State machine class
    """
    # from api.state_machine.state_machine_serializer import StateMachineSerializer
    return StateMachineSerializer.deserialize(definition)


def get_definition_func(definition_id):
    """
    Utility to fetch state machine definition and version from DB.
    Args:
        definition_id: Unique identifier for the state machine definition (_id).
    Returns:
        Tuple (definition, version) where version is _etag as string.
    """
    from flask import current_app as app
    db = app.data.driver.db
    sm_doc = db['statemachine'].find_one({'_id': definition_id})
    if not sm_doc:
        raise Exception(f"Statemachine definition not found for id: {definition_id}")
    return sm_doc['definition'], str(sm_doc.get('_etag', ''))

# Optionally, add TTL or periodic cleanup if needed.
