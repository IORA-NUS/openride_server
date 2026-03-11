import json
from flask import current_app as app
from eve.io.mongo import Validator
from eve.utils import config


class OpenRideValidator(Validator):
    """
        Custom validator for OpenRide platform data validation.

        Methods
        -------
        _validate_unique_in_list(unique_in_list, field, value)
            Validates that specified fields are unique within a list of objects.
            Reports errors for duplicate values found in the list.

        _validate_unique_combination(unique_combination, field, value)
            Validates that a combination of field values is unique across the resource.
            Ensures the combination does not exist elsewhere, excluding soft-deleted documents and the current document.

        _is_combination_unique(unique_combination, field, value, query)
            Helper method to check if a combination of field values is unique in the database.
            Handles resource configuration, soft deletion, and exclusion of the current document.
    """

    def _validate_unique_in_list(self, unique_in_list, field, value):
        """
        Validates that specified fields in a list of objects are unique.

        Args:
            unique_in_list (str or list): Field name(s) to check for uniqueness within each object in the list.
            field (str): The name of the field being validated (used for error reporting).
            value (list): The list of objects (typically dicts) to validate.

        Raises:
            Calls self._error with a formatted error message if any duplicates are found.

        Notes:
            - Supports checking uniqueness for multiple fields.
            - Handles both primitive and dictionary field values.
            - Reports all duplicate indices and their offending values.
        """
        """ {'type': 'list'} """
        # Enforce uniqueness of fields listed in unique_in_list against a
        # list of objects in value.
        # """
        # init error object
        errors = {}

        # force input to list
        fields_to_check = unique_in_list
        if type(fields_to_check) is not list:
            fields_to_check = [fields_to_check]

        for unique_field in fields_to_check:
            # build hash set
            hashes = []
            for i, channel in enumerate(value):
                if isinstance(channel, dict):
                    if unique_field in channel and isinstance(channel[unique_field], dict):
                        h = hash(frozenset(channel[unique_field].items()))
                    else:
                        h = hash(channel[unique_field])
                else:
                    h = hash(channel)
                hashes.append(h)

            # log duplicates
            seen_hashes = set()
            duplicate_hashes = set()
            for h in hashes:
                if h in seen_hashes:
                    duplicate_hashes.add(h)
                else:
                    seen_hashes.add(h)

            for i, h in enumerate(hashes):
                if h in duplicate_hashes:
                    if str(i) not in errors:
                        errors[str(i)] = {}
                    errors[str(i)] = {
                        'unique_field': f"value '{channel[unique_field] if isinstance(channel, dict) else str(channel)}' must be unique in list"
                    }

        # report errors
        if len(errors) > 0:
            formatted_errors = "; ".join(
                f"Index {index}: {details['unique_field']}" for index, details in errors.items()
            )
            self._error(field, f"Validation failed with the following errors: {formatted_errors}")


    def _validate_unique_combination(self, unique_combination, field, value):
        """
        Validates that the provided 'unique_combination' is a list of strings and that the 'value' is not None.
        If the validation passes, checks whether the combination of values specified by 'unique_combination' is unique
        within the context of the current document.

        Args:
            unique_combination (list): List of field names (strings) to check for uniqueness.
            field (str): The field being validated.
            value: The value of the field being validated.

        Raises:
            Adds an error to the field if 'unique_combination' is not a list of strings, if 'value' is None,
            or if an exception occurs during uniqueness validation.
        """
        """ {'type': 'list'} """
        if not isinstance(unique_combination, list) or not all(isinstance(item, str) for item in unique_combination):
            self._error(field, "'unique_combination' must be a list of strings")
            return

        if value is None:
            self._error(field, "'value' cannot be None")
            return
            query = {k: self.document.get(k, None) for k in unique_combination}
        try:
            self._is_combination_unique(unique_combination, field, value, {})
        except Exception as e:
            self._error(field, f"An error occurred during validation: {str(e)}")


    def _is_combination_unique(self, unique_combination, field, value, query):
        """
        Checks if a given combination of field values is unique within a resource.

        This method constructs a query based on the provided unique combination of fields,
        the specified field, and its value. It then checks the corresponding resource to
        determine if any existing document matches the combination, excluding soft-deleted
        documents and the current document (if updating). If a duplicate is found, an error
        is recorded for the field.

        Args:
            unique_combination (list): List of field names that must be unique together.
            field (str): The field being validated for uniqueness.
            value (Any): The value to check for uniqueness.
            query (dict): The initial query dictionary to be updated and used for uniqueness check.

        Returns:
            None
        """

        if unique_combination:
            query = {k: self.document[k] for k in unique_combination}
            query[field] = value

            if not self.resource or self.resource not in config.DOMAIN:
                self._error(field, f"Invalid resource: '{self.resource}'")
                return

            resource_config = config.DOMAIN[self.resource]

            # exclude soft deleted documents if applicable
            if resource_config.get('soft_delete', False):
                query[config.DELETED] = {'$ne': True}

            if self.document_id:
                id_field = resource_config.get('id_field')
                if id_field:
                    query[id_field] = {'$ne': self.document_id}
                else:
                    self._error(field, "Resource configuration is missing 'id_field'")

            datasource, _, _, _ = app.data.datasource(self.resource)

            if app.data.driver.db[datasource].find_one(query):
                self._error(field, f"value combination of '{', '.join(query.keys())}' is not unique")


