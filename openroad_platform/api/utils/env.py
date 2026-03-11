"""Simple helper to read environment variables
"""
import os


class Env:
    """
    Env is a utility class for accessing and parsing environment variables.
    Methods:
        env(variable_name, default=None):
            Retrieves the value of the specified environment variable.
            If the variable is not set, returns the provided default value.
        bool(variable_name, default='false'):
            Retrieves the value of the specified environment variable and parses it as a boolean.
            Returns True if the value (case-insensitive) is "t", "true", or "1"; otherwise, returns False.
            If the variable is not set, uses the provided default value.
        string(variable_name, default=''):
            Retrieves the value of the specified environment variable as a string.
            If the variable is not set, returns the provided default value.
        int(variable_name, default=None):
            Retrieves the value of the specified environment variable and parses it as an integer.
            If the variable is not set, uses the provided default value.
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
