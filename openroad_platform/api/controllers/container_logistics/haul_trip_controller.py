class HaulTripController:
    @classmethod
    def validate(cls, document, updates=None):
        updates = updates or {}
        statemachine_id = (
            (updates.get("statemachine") or {}).get("id")
            or (document.get("statemachine") or {}).get("id")
        )
        if not statemachine_id:
            raise Exception("statemachine_id is required for dynamic loading.")

        from api.utils.state_machine_cache import get_state_machine, get_definition_func

        StateMachineClass = get_state_machine(statemachine_id, get_definition_func)
        machine = StateMachineClass(start_value=document["state"])
        transition = updates.get("transition")

        if transition is not None:
            if not isinstance(transition, str):
                raise Exception(f"Transition must be a string, got {type(transition)}: {transition}")
            getattr(machine, transition)()

        updates["state"] = machine.current_state.name
        # Store feasible transitions list for debugging (optional field).
        try:
            updates["feasible_transitions"] = [t.event for t in machine.current_state.transitions]
        except Exception:
            pass

