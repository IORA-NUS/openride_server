from analytics.utils.grafana_pandas_datasource.registry import data_generators as dg

from .kpi_factory import KPIFactory
from .engine_factory import EngineFactory
from .trip_factory import TripFactory

def register_metric_readers():

    dg.add_metric_reader('revenue', KPIFactory.get_kpi_as_grafana_ts)
    dg.add_metric_reader('num_served', KPIFactory.get_kpi_as_grafana_ts)
    dg.add_metric_reader('num_cancelled', KPIFactory.get_kpi_as_grafana_ts)
    dg.add_metric_reader('wait_time_pickup', KPIFactory.get_kpi_as_grafana_ts)
    dg.add_metric_reader('wait_time_driver_confirm', KPIFactory.get_kpi_as_grafana_ts)
    dg.add_metric_reader('wait_time_total', KPIFactory.get_kpi_as_grafana_ts)
    dg.add_metric_reader('wait_time_assignment', KPIFactory.get_kpi_as_grafana_ts)
    dg.add_metric_reader('service_score', KPIFactory.get_kpi_as_grafana_ts)

    dg.add_metric_reader('passenger_requested_trip', TripFactory.get_location_as_grafana_table)
    dg.add_metric_reader('passenger_completed_trip', TripFactory.get_location_as_grafana_table)
    dg.add_metric_reader('passenger_cancelled_trip', TripFactory.get_location_as_grafana_table)

    dg.add_metric_reader('driver_looking_for_job', TripFactory.get_location_as_grafana_table)
    dg.add_metric_reader('driver_pickedup', TripFactory.get_location_as_grafana_table)

    dg.add_metric_reader('active_driver_count', TripFactory.get_active_agents_as_grafana_ts)
    dg.add_metric_reader('active_passenger_count', TripFactory.get_active_agents_as_grafana_ts)



    dg.add_metric_reader('revenue_step_obj', EngineFactory.get_solver_metric_as_grafana_ts)
    dg.add_metric_reader('pickup_step_obj', EngineFactory.get_solver_metric_as_grafana_ts)
    dg.add_metric_reader('service_step_obj', EngineFactory.get_solver_metric_as_grafana_ts)

    dg.add_metric_reader('revenue_weight', EngineFactory.get_solver_metric_as_grafana_ts)
    dg.add_metric_reader('pickup_weight', EngineFactory.get_solver_metric_as_grafana_ts)
    dg.add_metric_reader('service_weight', EngineFactory.get_solver_metric_as_grafana_ts)

    dg.add_metric_reader('revenue_perf', EngineFactory.get_solver_metric_as_grafana_ts)
    dg.add_metric_reader('pickup_perf', EngineFactory.get_solver_metric_as_grafana_ts)
    dg.add_metric_reader('service_perf', EngineFactory.get_solver_metric_as_grafana_ts)

    dg.add_metric_reader('all_solver_metrics', EngineFactory.get_solver_metric_as_grafana_ts)

def register_metric_finders():
    dg.add_metric_finder('run_id', KPIFactory.get_run_id)

    # print(f"{dg.metric_finders=}")

# def register_annotation_readers():
#     dg.add_annotation_reader('run_id_annotation', KPIFactory.get_run_id_annotation)

