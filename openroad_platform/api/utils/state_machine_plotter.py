
from graphviz import Digraph

def plot_state_machine(state_machine):
    """
    Generates and renders a state machine diagram using Graphviz.

    Args:
        state_machine: An object representing the state machine. It should have a `__name__` attribute,
            a `states` iterable, where each state has a `transitions` iterable. Each transition should have
            `source`, `destinations` (list), and `identifier` attributes.

    Side Effects:
        Creates and saves a PNG image of the state machine diagram in the 'state_transitions' directory,
        with the filename based on the state machine's name.

    Example:
        plot_state_machine(my_state_machine)
    """
    # print(state_machine.__name__)
    dg = Digraph(comment=state_machine.__name__, engine='dot')
    for s in state_machine.states:
        for t in s.transitions:
            dg.edge(t.source.name, t.destinations[0].name, label=t.identifier)
    dg.render('state_transitions/{}.gv'.format(state_machine.__name__), format='png')
