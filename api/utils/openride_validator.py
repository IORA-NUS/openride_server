import json
from flask import current_app as app
from eve.io.mongo import Validator
from eve.utils import config


class OpenRideValidator(Validator):

    def _validate_unique_in_list(self, unique_in_list, field, value):
        """ {'type': 'list'} """
        # Enforce uniqueness of fields listed in unique_in_list against a
        # list of objects in value.
        # """
        # init error object
        errors = {}

        # force input to list
        unique_fields = unique_in_list
        if type(unique_fields) is not list:
            unique_fields = [unique_fields]

        for unique_field in unique_fields:
            # build hash set
            hashes = []
            for i, channel in enumerate(value):
                if isinstance(channel, dict):
                    if isinstance(channel[unique_field], dict):
                        h = hash(frozenset(channel[unique_field].items()))
                    else:
                        h = hash(channel[unique_field])
                else:
                    h = hash(channel)
                hashes.append(h)

            # log duplicates
            for i, h in enumerate(hashes):
                if hashes.count(h) > 1:
                    if str(i) not in errors:
                        errors[str(i)] = {}
                    errors[str(i)] = {
                        'unique_field': f"value '{channel[unique_field] if isinstance(channel, dict) else str(channel)}' must be unique in list"
                    }

        # report errors
        if len(errors) > 0:
            self._error(field, json.dumps(errors))


    def _validate_unique_combination(self, unique_combination, field, value):
        """ {'type': 'list'} """
        self._is_combination_unique(unique_combination, field, value, {})


    def _is_combination_unique(self, unique_combination, field, value, query):
        """ Test if the value combination is unique.
        """
        if unique_combination:
            query = {k: self.document[k] for k in unique_combination}
            query[field] = value

            resource_config = config.DOMAIN[self.resource]

            # exclude soft deleted documents if applicable
            if resource_config['soft_delete']:
                query[config.DELETED] = {'$ne': True}

            if self.document_id:
                id_field = resource_config['id_field']
                query[id_field] = {'$ne': self.document_id}

            datasource, _, _, _ = app.data.datasource(self.resource)

            if app.data.driver.db[datasource].find_one(query):
                key_names = ', '.join([k for k in query])
                self._error(field, "value combination of '%s' is not unique" % key_names)


