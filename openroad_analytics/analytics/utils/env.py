"""Simple helper to read environment variables
"""
import os


class Env:

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
