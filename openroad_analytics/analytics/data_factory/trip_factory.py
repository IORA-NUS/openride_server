
import pandas as pd
from flask import current_app as app
from analytics.utils.grafana_pandas_datasource.util import dataframe_to_response, dataframe_to_json_table, annotations_to_response
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytz

class TripFactory():
    """
    TripFactory provides methods to query and process trip-related analytics data for ride-hailing simulations.

    Class Methods
    -------------
    get_location_as_grafana_table(run_id_list, state, ts_range, payload)
        Retrieves location data for a specific run and state, formatted as a Grafana-compatible table.

    get_location_by_state(run_id, state, ts_range)
        Queries the waypoint collection for location data filtered by run ID, state, and timestamp range. Returns a DataFrame with latitude and longitude.

    get_active_agents_as_grafana_ts(run_id_list, metric_name, ts_range, payload)
        Retrieves time series data of active agents (drivers or passengers) for specified runs and metrics, formatted for Grafana.

    get_active_agents(run_id_list, metric, ts_range, payload)
        Aggregates and computes the count of active agents (drivers or passengers) over time for given runs and metrics. Returns a pivoted DataFrame suitable for time series analysis.

    Notes
    -----
    - All methods assume access to a MongoDB database via `app.data.driver.db`.
    - Some queries may be slow and are recommended to be precomputed for performance.
    - Methods are designed to support analytics dashboards such as Grafana.
    """


    @classmethod
    def get_location_as_grafana_table(cls, run_id_list, state, ts_range, payload):
        """
        Retrieves location data for a specific run and state, formats it as a Grafana-compatible table.

        Args:
            run_id_list (list): List containing a single run ID.
            state (str): The state for which location data is requested.
            ts_range (tuple): A tuple specifying the time range for the query.
            payload (dict): Additional parameters for the query.

        Raises:
            Exception: If more than one run ID is provided in run_id_list.

        Returns:
            dict: Location data formatted as a Grafana table (JSON).
        """
        if len(run_id_list) != 1:
            raise Exception(f"This query only accepts 1 value for run_id. Got {run_id_list=}")

        df = cls.get_location_by_state(run_id_list[0], state, ts_range)

        result = dataframe_to_json_table(state, df)

        return result

    @classmethod
    def get_location_by_state(cls, run_id, state, ts_range):
        """
        Retrieves location data for waypoints matching a specific state and timestamp range within a simulation run.

        Args:
            run_id (str): The identifier for the simulation run.
            state (str): The state to filter waypoints by (e.g., 'active', 'completed').
            ts_range (dict or any): The timestamp range to filter waypoints (typically a MongoDB query operator).

        Returns:
            pd.DataFrame: A DataFrame indexed by 'sim_clock', containing columns for 'run_id', 'latitude', and 'longitude'.

        Notes:
            - The function queries the 'waypoint' collection in the database.
            - The resulting DataFrame includes latitude and longitude extracted from the event location coordinates.
            - The 'event' column is dropped from the final DataFrame.
        """
        ''' '''
        db = app.data.driver.db
        waypoint_collection = db['waypoint']

        filter = {
            'run_id': run_id,
            'sim_clock': ts_range,
            'event.state': state
        }
        projection = {
            "_id": 0,
            "sim_clock": 1,
            "run_id": 1,
            "event.location.coordinates": 1,
        }
        sort = list({
            'sim_clock': 1,
        }.items())

        cursor = waypoint_collection.find(filter,
                        projection=projection,
                        sort=sort)

        df = pd.DataFrame(list(cursor)) \
                .set_index('sim_clock', drop=True)

        df['latitude'] = [loc['location']['coordinates'][0] for loc in list(df['event'])]
        df['longitude'] = [loc['location']['coordinates'][1] for loc in list(df['event'])]

        df.drop(columns="event")

        return df

    @classmethod
    def get_active_agents_as_grafana_ts(cls, run_id_list, metric_name, ts_range, payload):
        """
        Retrieves active agent metrics for specified runs and formats the data as a Grafana-compatible time series response.

        Args:
            run_id_list (list): List of run IDs to query.
            metric_name (str): Name of the metric to retrieve.
            ts_range (tuple): Time range for the query, typically as (start, end).
            payload (dict): Additional parameters for filtering or specifying metric type.

        Returns:
            dict: Formatted time series data suitable for Grafana visualization.
        """

        df = cls.get_active_agents(run_id_list, metric_name, ts_range, payload)

        # if payload.get('type') not in ['value', 'cumulative', 'avg_by_time', 'avg_by_trip']:
        #     value_type = 'value'
        # else:
        #     value_type = payload.get('type')

        # df = pd.pivot_table(df,
        #                     index='sim_clock',
        #                     columns=['run_id', 'metric'],
        #                     values=value_type)
        # # print(df)
        # cols = [(run_id, metric_name) for run_id in run_id_list]
        # df = df[cols]

        result = dataframe_to_response(metric_name, df)

        return result

    @classmethod
    def get_active_agents(cls, run_id_list, metric, ts_range, payload):
        """
        Computes the number of active agents (drivers or passengers) over simulation time steps for given run IDs and metrics.

        This method aggregates agent entry and exit times from the database, calculates active counts at each simulation clock tick,
        and returns the results as a pivoted pandas DataFrame.

        Args:
            run_id_list (list): List of run IDs to include in the query.
            metric (str): Metric to compute, either 'active_driver_count' or 'active_passenger_count'.
            ts_range (dict): Dictionary specifying the time range with keys '$gt' and '$lte' as datetime objects.
            payload (dict): Additional options, including the output 'type' (e.g., 'value', 'cumulative', 'avg_by_time', 'avg_by_trip').

        Returns:
            pandas.DataFrame: Pivoted DataFrame indexed by simulation clock ticks, with columns for each (run_id, metric) pair,
                              containing the computed metric values.

        NOTE:
            This query can be slow and should ideally be moved to a precomputed KPI.
        """

        db = app.data.driver.db
        sim_step_size = 30

        total_seconds = ( ts_range['$lte'] - ts_range['$gt']).total_seconds()
        sim_clock_ticks = [ts_range['$gt'] + relativedelta(seconds=(step*sim_step_size)) for step in range(int((total_seconds//sim_step_size)))]

        # print(len(sim_clock_ticks))

        query = [
            {
                '$match': {
                    'run_id': {'$in': run_id_list},
                    'sim_clock': ts_range
                }
            }, {
                '$group': {
                    '_id': {
                        'user': '$user',
                        'run_id': '$run_id'
                    },
                    'entered_market': {
                        '$min': '$_created'
                    },
                    'exit_market': {
                        '$max': '$_updated'
                    }
                }
            }
        ]

        df = pd.DataFrame(columns=['sim_clock', 'run_id', 'metric', 'value']).astype({'value': 'int32'})

        if metric == 'active_driver_count':
            driver_collection = db.ridehail_driver_trip
            driver_cursor = driver_collection.aggregate(query)
            docs = list(driver_cursor)

        elif metric == 'active_passenger_count':
            pax_collection = db.ridehail_passenger_trip
            pax_cursor = pax_collection.aggregate(query)
            docs = list(pax_cursor)

        # for sim_clock in sim_clock_ticks:
        #     for run_id in run_id_list:

        #         value = 0
        #         for doc in docs:
        #             if (doc['_id']['run_id'] == run_id) and (doc['entered_market'] <= sim_clock) and (doc['exit_market'] >= sim_clock):
        #                 value += 1

        #         df = pd.concat([pd.DataFrame([[sim_clock, run_id, metric, value]],
        #                                      columns=df.columns),
        #                         df],ignore_index=True)

        metric_collection = {(sim_clock, run_id, metric): 0 for sim_clock in sim_clock_ticks for run_id in run_id_list}
        for run_id in run_id_list:
            for doc in docs:
                metric_collection[(doc['entered_market'], run_id, metric)] += 1
                metric_collection[(doc['exit_market'], run_id, metric)] -= 1

        df = pd.concat([pd.DataFrame([[k[0], k[1], k[2], v] for k, v in metric_collection.items()
                                        ], columns=df.columns),
                        df],ignore_index=True)

        df = df.groupby(['metric', 'run_id', 'sim_clock']).sum() \
                                    .groupby(level=1).cumsum().reset_index()



        df.sort_values(['run_id', 'metric', 'sim_clock'], inplace=True)

        if payload.get('type') not in ['value', 'cumulative', 'avg_by_time', 'avg_by_trip']:
            value_type = 'value'
        else:
            value_type = payload.get('type')

        df = pd.pivot_table(df,
                            index='sim_clock',
                            columns=['run_id', 'metric'],
                            values=value_type)
        # print(df)
        cols = [(run_id, metric) for run_id in run_id_list]
        df = df[cols]

        return df
