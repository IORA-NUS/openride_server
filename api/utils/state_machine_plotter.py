
from graphviz import Digraph

def plot_state_machine(state_machine):
    # print(state_machine.__name__)
    dg = Digraph(comment=state_machine.__name__, engine='dot')
    for s in state_machine.states:
        for t in s.transitions:
            dg.edge(t.source.name, t.destinations[0].name, label=t.identifier)
    dg.render('state_transitions/{}.gv'.format(state_machine.__name__), format='png')
