import os, logging
from unittest.mock import patch

from eve import Eve

from analytics.config import settings
from analytics.extensions import cors #, swagger
from eve_swagger import get_swagger_blueprint, add_documentation

from analytics.extensions import jwt

from analytics.views.auth import auth_view
from analytics.models import User

from analytics.views import (
    # GrafanaAnalyticsView,
    # #  GrafanaRunConfigView,
    # GrafanaAdminView,
    GrafanaView
)

from eve.io.mongo import validation

from analytics.data_factory.registry import register_metric_finders, register_metric_readers



def create_app(config=None, testing=False, cli=False):
    '''Application factory, used to create application
    '''
    # if using docker, monkey patch ensure_mongo_indexes
    # ENV DOCKER=true
    register_metric_finders()

    register_metric_readers()

    if os.environ.get('DOCKER'):
        with patch('eve.flaskapp.ensure_mongo_indexes') as mock_index_maker:
            mock_index_maker.return_value = 'Mocked'
            app = Eve(
                settings=get_settings_with_domain(),
                auth=auth_view.TokenAuth,
            )
    else:
        # logging.warning('Not Using Docker')
        app = Eve(
            settings=get_settings_with_domain(),
            auth=auth_view.TokenAuth,
        )


    configure_app(app, testing)
    configure_extensions(app, cli)
    register_blueprints(app)
    register_hooks(app)

    register_flask_classful_views(app)

    return app


def configure_app(app, testing=False):
    '''set configuration for application
    '''
    # default configuration
    app.config.from_object('analytics.config')

    if testing is True:
        # override with testing config
        app.config.from_object('analytics.configtest')
    else:
        # override with env variable, fail silently if not set
        app.config.from_envvar(
            'API_CONFIG', silent=True)


def configure_extensions(app, cli):
    '''configure flask extensions
    '''
    jwt.init_app(app)
    cors.init_app(app)



def get_settings_with_domain():
    settings['DOMAIN'] = {
        'user': User.model,
    }

    return settings

def register_blueprints(app):
    '''register all blueprints for application
    '''
    swagger = get_swagger_blueprint()
    app.register_blueprint(swagger)

    app.register_blueprint(auth_view.registrtion_bp)


def register_hooks(app):
    '''register all hooks for application
    '''



def register_flask_classful_views(app):
    ''' '''
    # GrafanaAnalyticsView.register(app)
    # # GrafanaRunConfigView.register(app)
    # GrafanaAdminView.register(app)

    GrafanaView.register(app)
