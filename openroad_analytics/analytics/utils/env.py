"""Simple helper to read environment variables
"""
import os


class Env:
    """
    Utility class for accessing environment variables with type conversion and default values.
    Methods
    -------
    env(variable_name, default=None)
        Retrieves the value of the specified environment variable. If not set, returns the provided default value.
    bool(variable_name, default='false')
        Retrieves the environment variable and converts it to a boolean. Accepts "t", "true", or "1" (case-insensitive) as True.
    string(variable_name, default='')
        Retrieves the environment variable as a string. Returns the default if not set.
    int(variable_name, default=None)
        Retrieves the environment variable and converts it to an integer. Returns the default if not set.
    """

    @staticmethod
    def env(variable_name, default=None):
        if default:
            return os.environ.get(variable_name, default=str(default))
        else:
            return os.environ.get(variable_name)

    @staticmethod
    def bool(variable_name, default='false'):
        var = Env.env(variable_name, default)
        if not var:
            var = str(default)

        return True if var.lower() in ("t", "true", "1") else False

    @staticmethod
    def string(variable_name, default=''):
        return Env.env(variable_name, default)

    @staticmethod
    def int(variable_name, default=None):
        return int(Env.env(variable_name, default))
