from analytics.utils.grafana_pandas_datasource.registry import data_generators as dg

from .kpi_factory import KPIFactory

def register_metric_readers():

    dg.add_metric_reader('revenue', KPIFactory.get_metric)
    dg.add_metric_reader('num_served', KPIFactory.get_metric)
    dg.add_metric_reader('num_cancelled', KPIFactory.get_metric)
    dg.add_metric_reader('wait_time_pickup', KPIFactory.get_metric)
    dg.add_metric_reader('wait_time_driver_confirm', KPIFactory.get_metric)
    dg.add_metric_reader('wait_time_total', KPIFactory.get_metric)
    dg.add_metric_reader('wait_time_assignment', KPIFactory.get_metric)
    dg.add_metric_reader('service_score', KPIFactory.get_metric)



def register_metric_finders():
    dg.add_metric_finder('run_id', KPIFactory.get_run_id)

    # print(f"{dg.metric_finders=}")
