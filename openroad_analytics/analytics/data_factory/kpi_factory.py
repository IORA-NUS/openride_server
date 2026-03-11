import pandas as pd
from flask import current_app as app
from analytics.utils.grafana_pandas_datasource.util import dataframe_to_response, dataframe_to_json_table, annotations_to_response

from analytics.utils import apply_transform

class KPIFactory():
    """
    Factory class for handling Key Performance Indicator (KPI) data retrieval and transformation.

    Attributes:
        metric_mapper (dict): Maps metric names to their corresponding database fields.
        run_id_mappers (dict): Maps run IDs to their descriptive names.

    Methods:
        get_run_id(*args):
            Retrieves the latest run configuration data from the database and returns it as a DataFrame.

        get_kpi_as_grafana_ts(run_id_list, metric_name, ts_range, payload):
            Fetches KPI time series data for specified run IDs and metric, transforms it for Grafana-compatible time series response.

        get_kpi_time_series(run_id_list, metric_list, ts_range, payload):
            Retrieves and processes KPI time series data for given run IDs and metrics, computes cumulative, average by time, and average by trip values, applies optional transformations, and returns a pivoted DataFrame.
    """

    metric_mapper = {
        'revenue' : 'revenue',
        'num_served' : 'num_served',
        'num_cancelled' : 'num_cancelled',
        'wait_time_pickup' : 'wait_time_pickup',
        'wait_time_driver_confirm' : 'wait_time_driver_confirm',
        'wait_time_total' : 'wait_time_total',
        'wait_time_assignment' : 'wait_time_assignment',
        'service_score' : 'service_score',

    }

    run_id_mappers = {
        'r0kZnIvJqUWg': 'Pickup Optimal',
        'sROLL5zudXBx': 'Revenue Optimal',
        '6OnGpMZ19V0k': 'Service Optimal',
        '2gp78vxu3j24': 'Compromise R1.2 P1.2 S1.2',
        'vr7zH3e1OGJc': 'Compromise R1.5 P1.2 S1.2',
        'JLpdE5GzvX1b': 'Compromise R1.5 P1.0 S1.0',
        'RGlocqBN8czZ': 'Compromise R1.5 P0.9 S0.9',
    }


    @classmethod
    def get_run_id(cls, *args):
        """
        Retrieves the latest run configuration records from the 'run_config' collection in the database.

        Args:
            *args: Variable length argument list (not used).

        Returns:
            pd.DataFrame: A DataFrame containing the selected fields ('run_id', 'name', 'value')
            from the latest run configuration records, sorted by the '_updated' timestamp in descending order.
        """

        db = app.data.driver.db
        run_config_collection = db['run_config']

        filter = {
        }
        projection = {
            "_id": 0,
            "run_id": 1, # Target should be part of the df
            "name": 1,
            "value": 1,
        }
        sort = list({
            '_updated': -1,
        }.items())

        cursor = run_config_collection.find(filter,
                        projection=projection,
                        sort=sort)

        df =  pd.DataFrame(list(cursor))
        result = dataframe_to_json_table('run_id', df)

        return df


    @classmethod
    def get_kpi_as_grafana_ts(cls, run_id_list, metric_name, ts_range, payload):
        """
        Retrieves KPI time series data for the specified metric and run IDs, formats it for Grafana time series visualization.

        Args:
            run_id_list (list): List of run IDs to retrieve KPI data for.
            metric_name (str): Name of the KPI metric to retrieve.
            ts_range (tuple or list): Time range for the KPI data (e.g., start and end timestamps).
            payload (dict): Additional parameters for data retrieval and transformation.

        Returns:
            dict: Formatted time series data suitable for Grafana visualization.
        """

        # print(run_id_list, metric_name, ts_range, payload)
        df = cls.get_kpi_time_series(run_id_list, [metric_name], ts_range, payload)
        # if payload.get('type') not in ['value', 'cumulative', 'avg_by_time', 'avg_by_trip']:
        #     value_type = 'value'
        # else:
        #     value_type = payload.get('type')

        # df = pd.pivot_table(df,
        #                     index='sim_clock',
        #                     columns=['run_id', 'metric'],
        #                     values=value_type)
        # cols = [(run_id, metric_name) for run_id in run_id_list]
        # df = df[cols]

        # df = apply_transform(df, list(df.columns), payload.get('transform'))
        result = dataframe_to_response(metric_name, df)

        return result


    @classmethod
    def get_kpi_time_series(cls, run_id_list, metric_list, ts_range, payload):
        """
        Generates a KPI time series DataFrame for specified runs and metrics.

        Retrieves KPI data from the MongoDB collection for the given run IDs and metrics within the specified time range.
        Computes cumulative values, average by time, and average by trip for each metric and run.
        Optionally adds the 'num_served' metric if not present to enable average calculations.
        Returns a pivoted DataFrame indexed by simulation clock, with columns for each (run_id, metric) pair,
        and values determined by the requested type ('value', 'cumulative', 'avg_by_time', 'avg_by_trip').
        Applies optional transformations to the resulting DataFrame.

        Args:
            run_id_list (list): List of run IDs to include in the time series.
            metric_list (list): List of metric names to retrieve and compute.
            ts_range (dict): MongoDB query for the simulation clock time range.
            payload (dict): Additional options, including:
                - 'type': Type of value to return ('value', 'cumulative', 'avg_by_time', 'avg_by_trip').
                - 'transform': Optional transformation to apply to the DataFrame.

        Returns:
            pandas.DataFrame: Pivoted DataFrame containing the requested KPI time series data.
        """
        db = app.data.driver.db
        collection = db.kpi
        add_num_served = False
        if 'num_served' not in metric_list:
            add_num_served = True
            metric_list.append('num_served')

        cursor = collection.find({
                'run_id': {'$in': run_id_list},
                'metric': {'$in': metric_list},
                'sim_clock': ts_range,
            },
            projection={ '_id': 0, 'run_id': 1, 'sim_clock': 1, 'metric': 1, 'value': 1,},
            sort=[('run_id', 1), ('metric', 1), ('sim_clock', 1)]
        )

        df = pd.DataFrame(list(cursor))
        df['cumulative'] = 0
        df['avg_by_time'] = 0
        df['avg_by_trip'] = 0


        time_step = None
        for run_id in run_id_list:
            num_served = df[(df['run_id'] == run_id) & (df['metric'] == 'num_served')]['value'].cumsum().tolist()
            if time_step is None:
                time_step = list(range(1, len(num_served)+1))

            for metric in metric_list:
                slice = (df['run_id'] == run_id) & (df['metric'] == metric)

                df.loc[slice, 'cumulative'] = df[slice]['value'].cumsum()
                df.loc[slice, 'avg_by_time'] = df[slice]['cumulative'] / time_step
                df.loc[slice, 'avg_by_trip'] = df[slice]['cumulative'] / num_served

        if add_num_served:
            df = df[df['metric'] != 'num_served']
            metric_list.remove('num_served')

        if payload.get('type') not in ['value', 'cumulative', 'avg_by_time', 'avg_by_trip']:
            value_type = 'value'
        else:
            value_type = payload.get('type')

        df = pd.pivot_table(df,
                            index='sim_clock',
                            columns=['run_id', 'metric'],
                            values=value_type)

        cols = [(run_id, metric) for run_id in run_id_list for metric in metric_list]
        df = df[cols]

        df = apply_transform(df, list(df.columns), payload.get('transform'))

        return df


