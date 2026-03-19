from datetime import datetime

class StateMachine:

    schema = {
        'name': {'type': 'string', 'required': True},
        'domain': {'type': 'string', 'required': True},
        'definition': {
            'type': 'dict',
            'required': True,
            'schema': {
                'states': {'type': 'list', 'required': True, 'minlength': 1, 'schema': {'type': 'string'}},
                'transitions': {'type': 'list', 'required': True, 'minlength': 1, 'schema': {'type': 'dict'}},
                'initial': {'type': 'string', 'required': True},
            }
        },
        # 'created_at': {'type': 'datetime', 'required': True, 'default': datetime.utcnow},
    }

    model = {
        'datasource': {'source': 'statemachine'},
        'url': 'statemachine',
        'schema': schema,
        'mongo_indexes': {
            'unique_name_simtype_index': (
                [
                    ('name', 1),
                    ('domain', 1),
                ],
                {'unique': True}
            ),
        },
        'resource_methods': ['GET', 'POST'],
        'item_methods': ['GET', 'PATCH'],
    }
