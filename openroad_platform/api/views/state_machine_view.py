from flask import abort
from api.utils.state_machine_cache import invalidate_state_machine

class StateMachineView:
    """
    Handles statemachine resource hooks for cache invalidation.
    """
    @classmethod
    def on_insert(cls, documents):
        """
        Invalidate cache for each inserted statemachine definition.
        """
        try:
            for doc in documents:
                definition_id = doc.get('_id') or doc.get('id')
                if definition_id:
                    invalidate_state_machine(definition_id)
        except Exception as e:
            abort(403, f"StateMachineView.on_insert error: {e}")

    @classmethod
    def on_update(cls, updates, document):
        """
        Invalidate cache for updated statemachine definition.
        """
        try:
            definition_id = document.get('_id') or document.get('id')
            if definition_id:
                invalidate_state_machine(definition_id)
        except Exception as e:
            abort(403, f"StateMachineView.on_update error: {e}")
