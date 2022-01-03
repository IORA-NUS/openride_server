import pandas as pd
from flask import current_app as app
from analytics.utils.grafana_pandas_datasource.util import dataframe_to_response, dataframe_to_json_table, annotations_to_response

from analytics.utils import apply_transform


class EngineFactory():

    metric_mapper = {
        'revenue_step_obj' : 'realtime_revenue_step',
        'pickup_step_obj' : 'realtime_reverse_pickup_time_step',
        'service_step_obj' : 'realtime_service_score_step',

        'revenue_weight' : 'weight_revenue',
        'pickup_weight' : 'weight_pickup_time',
        'service_weight' : 'weight_service_score',

        'revenue_perf' : 'revenue_perf',
        'pickup_perf' : 'pickup_perf',
        'service_perf' : 'service_perf',

    }


    @classmethod
    def get_solver_metric_as_grafana_ts(cls, run_id_list, metric_name, ts_range, payload):
        ''''''
        df = cls.get_solver_metric_time_series(run_id_list, metric_name, ts_range, payload)
        # if payload.get('type') not in ['value', 'cumulative', 'avg_by_time', 'avg_by_trip']:
        #     value_type = 'value'
        # else:
        #     value_type = payload.get('type')

        # df = pd.pivot_table(df,
        #                     index='sim_clock',
        #                     columns=['run_id', 'engine_name', 'metric'],
        #                     values=value_type)

        # if metric_name != 'all_solver_metrics':
        #     ''' '''
        #     df = df[[c for c in list(df.columns) if cls.metric_mapper[metric_name] in c]]


        # df = apply_transform(df, list(df.columns), payload.get('transform'))
        result = dataframe_to_response(metric_name, df)

        return result



    @classmethod
    def get_solver_metric_time_series(cls, run_id_list, metric_name, ts_range, payload):
        ''''''
        db = app.data.driver.db
        collection = db['engine_history']
        # formula = payload.get('formula')

        if len(run_id_list) != 1:
            raise Exception(f"This query only accepts 1 value for run_id. Got {run_id_list=}")

        aggregation = [
            {
                '$match': {
                    'run_id': {"$in": run_id_list},
                    'sim_clock': ts_range
                }
            }, {
                '$lookup': {
                    'from': 'engine',
                    'localField': 'engine',
                    'foreignField': '_id',
                    'as': 'engine'
                }
            }, {
                '$project': {
                    "_id": 0,
                    "run_id": 1,
                    "sim_clock": 1,
                    'online_params': 1,
                    'engine_name': {
                        '$arrayElemAt': [
                            '$engine.name', 0
                        ]
                    },
                }
            }, {
                '$sort': {
                    'run_id': 1,
                    'engine_name': 1,
                    'sim_clock': 1
                }
            }
        ]

        cursor = collection.aggregate(aggregation)

        df = pd.DataFrame(list(cursor))
        df = pd.concat([df.drop(['online_params'], axis=1), df['online_params'].apply(pd.Series)], axis=1)


        try:
            df['pickup_perf'] = 100* df['realtime_reverse_pickup_time_cum'] / df['exp_target_reverse_pickup_time']
        except:
            df['pickup_perf'] = 0

        try:
            df['revenue_perf'] = 100* df['realtime_revenue_cum'] / df['exp_target_revenue']
        except:
            df['revenue_perf'] = 0

        try:
            df['service_perf'] = 100* df['realtime_service_score_cum'] / df['exp_target_service_score']
        except:
            df['service_perf'] = 0

        df = df.melt(id_vars=['sim_clock', 'run_id', 'engine_name'],
                     var_name='metric', value_name='value')


        if payload.get('type') not in ['value', 'cumulative', 'avg_by_time', 'avg_by_trip']:
            value_type = 'value'
        else:
            value_type = payload.get('type')

        df = pd.pivot_table(df,
                            index='sim_clock',
                            columns=['run_id', 'engine_name', 'metric'],
                            values=value_type)

        if metric_name != 'all_solver_metrics':
            ''' '''
            df = df[[c for c in list(df.columns) if cls.metric_mapper[metric_name] in c]]


        df = apply_transform(df, list(df.columns), payload.get('transform'))


        return df

