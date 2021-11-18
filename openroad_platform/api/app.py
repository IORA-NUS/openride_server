
from eve import Eve
from api.config import settings
from api.extensions import cors #, swagger
from eve_swagger import get_swagger_blueprint, add_documentation

from api.extensions import jwt

from api.models import (User,
                        Driver, #RideHailDriverTrip,
                        Vehicle,
                        Passenger, #RideHailPassengerTrip,
                        Waypoint,
                        Kpi,
                        Engine, EngineHistory,
                        DriverRideHailTrip, PassengerRideHailTrip,
                        RunConfig,
                    )

from api.views.auth import auth_view
from api.views.admin import admin_view

from api.views import (UserView, #user_bp,
                        DriverView, #DriverTripView,
                        PassengerView, #PassengerTripView,
                        VehicleView, #vehicle_bp,
                        WaypointView, WaypointHistoryView,
                        KpiView, KpiHistoryView,
                        EngineView, EngineHistoryView,
                        DriverRideHailTripView, PassengerRideHailTripView,
                        DriverRideHailTripWorkflowView, PassengerRideHailTripWorkflowView,
                        # DriverRideHailTripCollectionView, PassengerRideHailTripCollectionView,
                    )

# from api.views import (DriverTripWorkflowView, PassengerTripWorkflowView)
# from api.views import DriverTripBP

from api.utils import OpenRideValidator #, add_user_on_insert
from api.utils import swaggerify, generate_everything

from eve.io.mongo import validation

# import flask_monitoringdashboard as dashboard
from prometheus_flask_exporter import PrometheusMetrics


def create_app(config=None, testing=False, cli=False):
    '''Application factory, used to create application
    '''
    app = Eve(
        settings=get_settings_with_domain(),
        auth=auth_view.TokenAuth,
        validator=OpenRideValidator
    )

    configure_app(app, testing)
    configure_extensions(app, cli)
    register_blueprints(app)
    register_hooks(app)

    # app.add_route('/plot_state_machines', state_machine_plotter())

    register_flask_classful_views(app)

    # dashboard.bind(app)
    metrics = PrometheusMetrics(app)
    metrics.info('Openroad', 'OpenRoad API', version='0.0.1')

    # print(app.url_map)

    # swaggerify(app, 'OpenRide_ClassyViews', '0.1.0', swagger_path='/swagger.json')


    return app


def configure_app(app, testing=False):
    '''set configuration for application
    '''
    # default configuration
    app.config.from_object('api.config')

    if testing is True:
        # override with testing config
        app.config.from_object('api.configtest')
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
        # 'register_user': User.registration_model,
        'driver': Driver.model,
        'vehicle': Vehicle.model,
        'passenger': Passenger.model,

        'driver_ride_hail_trip': DriverRideHailTrip.model,
        'passenger_ride_hail_trip': PassengerRideHailTrip.model,

        'waypoint': Waypoint.model,
        'trip_waypoints': Waypoint.trip_waypoints,

        'kpi': Kpi.model,
        'metric': Kpi.metric,

        'engine': Engine.model,
        'engine_history': EngineHistory.model,

        'run_config': RunConfig.model
    }

    return settings

def register_blueprints(app):
    '''register all blueprints for application
    '''
    swagger = get_swagger_blueprint()
    app.register_blueprint(swagger)

    app.register_blueprint(auth_view.registrtion_bp)
    app.register_blueprint(admin_view.blueprint)

    # app.register_blueprint(user_bp)
    # app.register_blueprint(vehicle_bp)
    # app.register_blueprint(DriverView.blueprint)
    # app.register_blueprint(DriverTripView.DriverTripBP)

    # add_documentation(swagger, {'paths': {'/status': {'get': {'parameters': [
    #     {
    #         'in': 'query',
    #         'name': 'foobar',
    #         'required': False,
    #         'description': 'special query parameter',
    #         'type': 'string'
    #     }]
    # }}}})

    # add_documentation(swagger, generate_everything(app, 'test', '1.0'))


def register_hooks(app):
    '''register all hooks for application
    '''
    # app.on_insert += add_user_on_insert
    # app.on_pre_PATCH += User.pre_patch_callback

    # app.on_pre_GET_user += UserView.pre_GET_callback
    app.on_update_user += UserView.on_update

    # app.on_pre_POST_driver += DriverView.pre_POST_callback
    app.on_insert_driver += DriverView.on_insert
    app.on_update_driver += DriverView.on_update

    # app.on_pre_POST_passenger += PassengerView.pre_POST_callback
    app.on_insert_passenger += PassengerView.on_insert
    app.on_update_passenger += PassengerView.on_update

    app.on_insert_vehicle += VehicleView.on_insert
    app.on_update_vehicle += VehicleView.on_update

    app.on_insert_driver_ride_hail_trip += DriverRideHailTripView.on_insert
    app.on_update_driver_ride_hail_trip += DriverRideHailTripView.on_update
    app.on_inserted_driver_ride_hail_trip += DriverRideHailTripView.on_inserted
    app.on_updated_driver_ride_hail_trip += DriverRideHailTripView.on_updated

    app.on_insert_passenger_ride_hail_trip += PassengerRideHailTripView.on_insert
    app.on_update_passenger_ride_hail_trip += PassengerRideHailTripView.on_update
    app.on_inserted_passenger_ride_hail_trip += PassengerRideHailTripView.on_inserted
    app.on_updated_passenger_ride_hail_trip += PassengerRideHailTripView.on_updated

    app.on_insert_waypoint += WaypointView.on_insert
    # app.on_fetched_resource_waypoint += WaypointView.on_fetched

    app.on_insert_kpi += KpiView.on_insert

    app.on_insert_engine += EngineView.on_insert
    app.on_update_engine += EngineView.on_update
    app.on_updated_engine += EngineView.on_updated

    app.on_insert_engine_history += EngineHistoryView.on_insert


def register_flask_classful_views(app):
    ''' '''
    DriverRideHailTripWorkflowView.register(app)
    # DriverRideHailTripCollectionView.register(app)

    PassengerRideHailTripWorkflowView.register(app)
    # PassengerRideHailTripCollectionView.register(app)

    WaypointHistoryView.register(app)
    KpiHistoryView.register(app)
