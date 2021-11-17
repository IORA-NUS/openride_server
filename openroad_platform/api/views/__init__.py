# from .auth import *

from .driver_view import DriverView
from .passenger_view import PassengerView
# from .driver_trip_view import DriverTripView, DriverTripWorkflowView
# from .passenger_trip_view import PassengerTripView, PassengerTripWorkflowView

from .ride_hail import (DriverRideHailTripView,
                        DriverRideHailTripWorkflowView,
                        # DriverRideHailTripCollectionView,
                        PassengerRideHailTripView,
                        PassengerRideHailTripWorkflowView,
                        # PassengerRideHailTripCollectionView
                        )

from .user_view import UserView #, user_bp
from .vehicle_view import VehicleView #, vehicle_bp

from .waypoint_view import WaypointView, WaypointHistoryView

from .engine_view import EngineView
from .engine_history_view import EngineHistoryView

from .kpi_view import KpiView, KpiHistoryView
