from analytics.utils.grafana_pandas_datasource.registry import data_generators as dg

from .kpi_factory import KPIFactory
from .engine_factory import EngineFactory
from .trip_factory import TripFactory

def register_metric_readers():

    dg.add_metric_reader('revenue', KPIFactory.get_metric)
    dg.add_metric_reader('num_served', KPIFactory.get_metric)
    dg.add_metric_reader('num_cancelled', KPIFactory.get_metric)
    dg.add_metric_reader('wait_time_pickup', KPIFactory.get_metric)
    dg.add_metric_reader('wait_time_driver_confirm', KPIFactory.get_metric)
    dg.add_metric_reader('wait_time_total', KPIFactory.get_metric)
    dg.add_metric_reader('wait_time_assignment', KPIFactory.get_metric)
    dg.add_metric_reader('service_score', KPIFactory.get_metric)

    dg.add_metric_reader('revenue_per_trip', KPIFactory.get_metric_rate)
    dg.add_metric_reader('num_served_per_trip', KPIFactory.get_metric_rate)
    dg.add_metric_reader('num_cancelled_per_trip', KPIFactory.get_metric_rate)
    dg.add_metric_reader('wait_time_pickup_per_trip', KPIFactory.get_metric_rate)
    dg.add_metric_reader('wait_time_driver_confirm_per_trip', KPIFactory.get_metric_rate)
    dg.add_metric_reader('wait_time_total_per_trip', KPIFactory.get_metric_rate)
    dg.add_metric_reader('wait_time_assignment_per_trip', KPIFactory.get_metric_rate)
    dg.add_metric_reader('service_score_per_trip', KPIFactory.get_metric_rate)

    dg.add_metric_reader('passenger_pickup', TripFactory.get_passenger_trip_pickup_location)
    dg.add_metric_reader('passenger_dropoff', TripFactory.get_passenger_trip_dropoff_location)

    dg.add_metric_reader('driver_available', TripFactory.get_driver_available_location)


    dg.add_metric_reader('revenue_step_obj', EngineFactory.get_metric)
    dg.add_metric_reader('pickup_step_obj', EngineFactory.get_metric)
    dg.add_metric_reader('service_step_obj', EngineFactory.get_metric)

    # dg.add_metric_reader('revenue_obj_pct', EngineFactory.get_metric)
    # dg.add_metric_reader('pickup_obj_pct', EngineFactory.get_metric)
    # dg.add_metric_reader('service_obj_pct', EngineFactory.get_metric)

    # dg.add_metric_reader('revenue_step_tgt', EngineFactory.get_static_metric)
    # dg.add_metric_reader('pickup_step_tgt', EngineFactory.get_static_metric)
    # dg.add_metric_reader('service_step_tgt', EngineFactory.get_static_metric)

    dg.add_metric_reader('revenue_weight', EngineFactory.get_metric)
    dg.add_metric_reader('pickup_weight', EngineFactory.get_metric)
    dg.add_metric_reader('service_weight', EngineFactory.get_metric)

    dg.add_metric_reader('all_solver_metrics', EngineFactory.get_all_solver_metrics)

def register_metric_finders():
    dg.add_metric_finder('run_id', KPIFactory.get_run_id)

    # print(f"{dg.metric_finders=}")

# def register_annotation_readers():
#     dg.add_annotation_reader('run_id_annotation', KPIFactory.get_run_id_annotation)

