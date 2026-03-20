

statemachine_schema = {
    'name': {
        'type': 'string',
        'required': False,
        'default': None
    },
    'domain': {
        'type': 'string',
        'required': False,
        'default': None
    },
    'id': {
        'type': 'objectid',
        'required': False,
        'data_relation': {
            'resource': 'statemachine',
            'field': '_id'
        },
        # 'default': None
        'readonly': True
    },
}

persona_schema = {
    'role': {
        'type': 'string',
        'required': True,
        'default': None
    },
    'domain': {
        'type': 'string',
        'required': True,
        'default': None
    }
}
