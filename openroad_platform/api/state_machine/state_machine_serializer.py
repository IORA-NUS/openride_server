

from statemachine import State, StateMachine

class StateMachineSerializer:
    """
    Utility class to serialize and deserialize state machines.
    - deserialize(definition): builds a StateMachine class from definition
    - serialize(sm_cls): serializes a StateMachine class to definition
    """
    @staticmethod
    def deserialize(definition):
        states = {}
        initial = definition['initial']
        # Determine which states are final (targets that are never sources)
        all_sources = set()
        all_targets = set()
        for t in definition['transitions']:
            sources = t['source']
            if not isinstance(sources, list):
                sources = [sources]
            all_sources.update(sources)
            all_targets.add(t['target'])
        final_states = all_targets - all_sources

        # Create State objects
        for state in definition['states']:
            if isinstance(state, dict):
                name = state['id']
                label = state.get('label', state['id'])
                is_initial = (name == initial)
                is_final = name in final_states
                states[name] = State(label, initial=is_initial, final=is_final)
            else:
                name = state
                is_initial = (name == initial)
                is_final = name in final_states
                states[name] = State(name, initial=is_initial, final=is_final)

        # Debug print states and transitions
        print("[DEBUG] States:", list(states.keys()))
        print("[DEBUG] Initial:", initial)
        print("[DEBUG] Transitions:")
        for t in definition['transitions']:
            print("  ", t)

        # Build class dict with states as class attributes
        class_dict = {name: state for name, state in states.items()}

        # Attach each transition as a unique method (trigger_source_target)
        for t in definition['transitions']:
            trigger = t['trigger']
            sources = t['source']
            target = t['target']
            if not isinstance(sources, list):
                sources = [sources]
            for src in sources:
                method_name = f"{trigger}__{src}__{target}"
                class_dict[method_name] = getattr(states[src], 'to')(states[target])

        # Compose all transitions for each trigger so main trigger works from all valid sources
        trigger_map = {}
        for t in definition['transitions']:
            trigger = t['trigger']
            sources = t['source']
            target = t['target']
            if not isinstance(sources, list):
                sources = [sources]
            for src in sources:
                method = getattr(states[src], 'to')(states[target])
                if trigger not in trigger_map:
                    trigger_map[trigger] = method
                else:
                    trigger_map[trigger] = trigger_map[trigger] | method
        for trigger, composed in trigger_map.items():
            class_dict[trigger] = composed

        # Dynamically create a StateMachine subclass with states and transitions attached
        DynamicSM = type("DynamicSM", (StateMachine,), class_dict)
        return DynamicSM

    @staticmethod
    def serialize(sm_cls):
        sm = sm_cls()
        states = [state.name for state in sm.states]
        transitions = []
        for state in sm.states:
            for transition in getattr(state, 'transitions', []):
                trigger = getattr(transition, 'trigger', None)
                event = getattr(transition, 'event', None)
                transitions.append({
                    'trigger': trigger or event or '',
                    'source': state.name,
                    'target': transition.target.name,
                })
        initial = None
        for state in sm.states:
            if state.initial:
                initial = state.name
                break
        return {
            'states': states,
            'transitions': transitions,
            'initial': initial,
        }

# Example usage:
if __name__ == '__main__':

    def print_state(sm):
        print(sm.configuration[0].id)

    definition = {
        "states": ["idle", "running", "finished"],
        "transitions": [
            {"trigger": "start", "source": "idle", "target": "running"},
            {"trigger": "finish", "source": "running", "target": "finished"}
        ],
        "initial": "idle"
    }
    DynamicSM = StateMachineSerializer.deserialize(definition)
    sm = DynamicSM()
    print_state(sm)  # 'idle'
    sm.start()
    print_state(sm)  # 'running'
    sm.finish()
    print_state(sm)  # 'finished'

    # Serialize back
    serialized = StateMachineSerializer.serialize(DynamicSM)
    print("[SERIALIZED]", serialized)

    definition = {
        "states": [
            "driver_init_trip",
            "driver_looking_for_job",
            "driver_received_trip",
            "driver_rejected_trip",
            "driver_accepted_trip",
            "driver_cancelled_trip",
            "driver_moving_to_pickup",
            "driver_waiting_to_pickup",
            "driver_pickedup",
            "driver_moving_to_dropoff",
            "driver_waiting_to_dropoff",
            "driver_droppedoff",
            "driver_completed_trip"
        ],
        "transitions": [
            {"trigger": "look_for_job", "source": "driver_init_trip", "target": "driver_looking_for_job"},
            {"trigger": "recieve", "source": "driver_init_trip", "target": "driver_received_trip"},
            {"trigger": "end_trip", "source": "driver_init_trip", "target": "driver_completed_trip"},
            {"trigger": "force_quit", "source": "driver_init_trip", "target": "driver_cancelled_trip"},
            {"trigger": "end_trip", "source": "driver_looking_for_job", "target": "driver_completed_trip"},
            {"trigger": "cancel", "source": "driver_looking_for_job", "target": "driver_cancelled_trip"},
            {"trigger": "force_quit", "source": "driver_looking_for_job", "target": "driver_cancelled_trip"},
            {"trigger": "confirm", "source": "driver_received_trip", "target": "driver_accepted_trip"},
            {"trigger": "reject", "source": "driver_received_trip", "target": "driver_rejected_trip"},
            {"trigger": "force_quit", "source": "driver_received_trip", "target": "driver_cancelled_trip"},
            {"trigger": "end_trip", "source": "driver_rejected_trip", "target": "driver_completed_trip"},
            {"trigger": "force_quit", "source": "driver_rejected_trip", "target": "driver_cancelled_trip"},
            {"trigger": "passenger_confirmed_trip", "source": "driver_accepted_trip", "target": "driver_moving_to_pickup"},
            {"trigger": "passenger_cancelled_trip", "source": "driver_accepted_trip", "target": "driver_completed_trip"},
            {"trigger": "cancel", "source": "driver_accepted_trip", "target": "driver_cancelled_trip"},
            {"trigger": "force_quit", "source": "driver_accepted_trip", "target": "driver_cancelled_trip"},
            {"trigger": "wait_to_pickup", "source": "driver_moving_to_pickup", "target": "driver_waiting_to_pickup"},
            {"trigger": "passenger_cancelled_trip", "source": "driver_moving_to_pickup", "target": "driver_completed_trip"},
            {"trigger": "cancel", "source": "driver_moving_to_pickup", "target": "driver_cancelled_trip"},
            {"trigger": "force_quit", "source": "driver_moving_to_pickup", "target": "driver_cancelled_trip"},
            {"trigger": "passenger_cancelled_trip", "source": "driver_waiting_to_pickup", "target": "driver_completed_trip"},
            {"trigger": "passenger_acknowledge_pickup", "source": "driver_waiting_to_pickup", "target": "driver_pickedup"},
            {"trigger": "cancel", "source": "driver_waiting_to_pickup", "target": "driver_cancelled_trip"},
            {"trigger": "force_quit", "source": "driver_waiting_to_pickup", "target": "driver_cancelled_trip"},
            {"trigger": "move_to_dropoff", "source": "driver_pickedup", "target": "driver_moving_to_dropoff"},
            {"trigger": "force_quit", "source": "driver_pickedup", "target": "driver_cancelled_trip"},
            {"trigger": "wait_to_dropoff", "source": "driver_moving_to_dropoff", "target": "driver_waiting_to_dropoff"},
            {"trigger": "force_quit", "source": "driver_moving_to_dropoff", "target": "driver_cancelled_trip"},
            {"trigger": "passenger_acknowledge_dropoff", "source": "driver_waiting_to_dropoff", "target": "driver_droppedoff"},
            {"trigger": "force_quit", "source": "driver_waiting_to_dropoff", "target": "driver_cancelled_trip"},
            {"trigger": "end_trip", "source": "driver_droppedoff", "target": "driver_completed_trip"},
            {"trigger": "force_quit", "source": "driver_droppedoff", "target": "driver_cancelled_trip"}
        ],
        "initial": "driver_init_trip"
    }

    DynamicSM = StateMachineSerializer.deserialize(definition)
    sm = DynamicSM()

    # Simulate a full trip lifecycle
    print_state(sm)  # 'driver_init_trip'
    sm.look_for_job()
    print_state(sm)  # 'driver_looking_for_job'
    sm.end_trip()
    print_state(sm)  # 'driver_completed_trip'

    # Reset and test more transitions
    sm = DynamicSM()
    print("\n--- New Trip ---")
    print_state(sm)  # 'driver_init_trip'
    sm.recieve()
    print_state(sm)  # 'driver_received_trip'
    sm.confirm()
    print_state(sm)  # 'driver_accepted_trip'
    sm.passenger_confirmed_trip()
    print_state(sm)  # 'driver_moving_to_pickup'
    sm.wait_to_pickup()
    print_state(sm)  # 'driver_waiting_to_pickup'
    sm.passenger_acknowledge_pickup()
    print_state(sm)  # 'driver_pickedup'
    sm.move_to_dropoff()
    print_state(sm)  # 'driver_moving_to_dropoff'
    sm.wait_to_dropoff()
    print_state(sm)  # 'driver_waiting_to_dropoff'
    sm.passenger_acknowledge_dropoff()
    print_state(sm)  # 'driver_droppedoff'
    sm.end_trip()
    print_state(sm)  # 'driver_completed_trip'
