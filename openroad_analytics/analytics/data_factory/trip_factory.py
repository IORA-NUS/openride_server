
import pandas as pd
from flask import current_app as app
from analytics.utils.grafana_pandas_datasource.util import dataframe_to_response, dataframe_to_json_table, annotations_to_response
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytz

class TripFactory():


    @classmethod
    def get_location_as_grafana_table(cls, run_id_list, state, ts_range, payload):
        if len(run_id_list) != 1:
            raise Exception(f"This query only accepts 1 value for run_id. Got {run_id_list=}")

        df = cls.get_location_by_state(run_id_list[0], state, ts_range)

        result = dataframe_to_json_table(state, df)

        return result

    @classmethod
    def get_location_by_state(cls, run_id, state, ts_range):
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
        ''' NOTE: This should be moved to a precomputed KPI as this query can be rather slow'''

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
            driver_collection = db.driver_ride_hail_trip
            driver_cursor = driver_collection.aggregate(query)
            docs = list(driver_cursor)

        elif metric == 'active_passenger_count':
            pax_collection = db.passenger_ride_hail_trip
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
