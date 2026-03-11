from statemachine import State, StateMachine


class UserStateMachine(StateMachine):
    """
    UserStateMachine defines the workflow for a user's state transitions within the platform.

    States:
        - dormant: The initial state where the user is inactive.
        - active: The state where the user is active.

    Transitions:
        - register: Moves the user from dormant to active.
        - deregister: Moves the user from active back to dormant.
    """

    dormant = State('dormant', initial=True)
    # activation_requested = State('activation_requested')
    # activation_sent = State('activation_sent')
    # activation_failed = State('activation_failed')
    active = State('active')

    register = dormant.to(active)
    deregister = active.to(dormant)

class WorkflowStateMachine(StateMachine):
    """
    WorkflowStateMachine defines the state transitions for an agent's workflow.

    States:
        - dormant: Initial state, agent is inactive.
        - offline: Agent is registered but not online.
        - online: Agent is actively online.

    Transitions:
        - register: Moves agent from 'dormant' to 'offline'.
        - deregister: Moves agent from 'offline' to 'dormant'.
        - login: Moves agent from 'offline' to 'online'.
        - logout: Moves agent from 'online' to 'offline'.
    """

    dormant = State('dormant', initial=True)
    offline = State('offline')
    online = State('online')

    register = dormant.to(offline)
    deregister = offline.to(dormant)
    login = offline.to(online)
    logout = offline.from_(online)



