import pandas as pd
from flask import current_app as app
from analytics.utils.grafana_pandas_datasource.util import dataframe_to_response, dataframe_to_json_table, annotations_to_response


class EngineFactory():

    metric_mapper = {
        'revenue_step_obj' : 'realtime_revenue_step',
        'pickup_step_obj' : 'realtime_reverse_pickup_time_step',
        'service_step_obj' : 'realtime_service_score_step',

        # 'revenue_obj_pct' : 'realtime_revenue_step',
        # 'pickup_obj_pct' : 'realtime_reverse_pickup_time_step',
        # 'service_obj_pct' : 'realtime_service_score_step',

        # 'revenue_step_tgt' : 'exp_target_revenue',
        # 'pickup_step_tgt' : 'exp_target_reverse_pickup_time',
        # 'service_step_tgt' : 'exp_target_service_score',

        'revenue_weight' : 'weight_revenue',
        'pickup_weight' : 'weight_pickup_time',
        'service_weight' : 'weight_service_score',

    }


    @classmethod
    def get_all_solver_metrics(cls, run_id_list, metric_name, ts_range, payload):
        ''''''
        db = app.data.driver.db
        kpi_collection = db['engine_history']
        formula = payload.get('formula')

        if len(run_id_list) != 1:
            raise Exception(f"This query only accepts 1 value for run_id. Got {run_id_list=}")

        filter = {
            'run_id': {"$in": run_id_list},
            # 'metric': cls.metric_mapper[metric_name],
            'sim_clock': ts_range
        }
        projection = {
            "_id": 0,
            "sim_clock": 1,
            "online_params": 1,
            "runtime_performance": 1,
        }
        sort = list({
            'sim_clock': 1,
        }.items())

        cursor = kpi_collection.find(filter,
                        projection=projection,
                        sort=sort)

        df = pd.DataFrame(list(cursor))
        df = pd.concat([df.drop(['online_params'], axis=1), df['online_params'].apply(pd.Series)], axis=1)
        df = pd.concat([df.drop(['runtime_performance'], axis=1), df['runtime_performance'].apply(pd.Series)], axis=1)
        df = df.set_index('sim_clock', drop=True)

        df['realtime_reverse_pickup_time_cum_rate'] = 100* df['realtime_reverse_pickup_time_cum'] / df['exp_target_reverse_pickup_time']
        df['realtime_revenue_cum_rate'] = 100* df['realtime_revenue_cum'] / df['exp_target_revenue']
        df['realtime_service_score_cum_rate'] = 100* df['realtime_service_score_cum'] / df['exp_target_service_score']

        # print(df)
        # print(df.columns)

        result = dataframe_to_response(metric_name, df)

        # df['metric'] = cls.metric_mapper[metric_name]
        # result = dataframe_to_json_table(metric_name, cls.apply_formula(df, cls.metric_mapper[metric_name], formula))

        return result


    @classmethod
    def get_metric(cls, run_id_list, metric_name, ts_range, payload):
        ''''''

        # # if payload.get('compare', False):
        # if len(run_id_list) > 1:
        #     return cls.get_metric_cmp(run_id_list, metric_name, ts_range, payload)
        # else:
        #     return cls.get_metric_as_is(run_id_list, metric_name, ts_range, payload)

        return cls.get_metric_as_is(run_id_list, metric_name, ts_range, payload)



    @classmethod
    def get_static_metric(cls, run_id_list, metric_name, ts_range, payload):
        ''''''
        # # if payload.get('compare', False):
        # if len(run_id_list) > 1:
        #     return cls.get_metric_rate_cmp(run_id_list, metric_name, ts_range, payload)
        # else:
        #     return cls.get_metric_rate_as_is(run_id_list, metric_name, ts_range, payload)
        return cls.get_static_metric_as_is(run_id_list, metric_name, ts_range, payload)


    @classmethod
    def get_metric_as_is(cls, run_id_list, metric_name, ts_range, payload):
        ''''''
        db = app.data.driver.db
        kpi_collection = db['engine_history']
        formula = payload.get('formula')

        if len(run_id_list) != 1:
            raise Exception(f"This query only accepts 1 value for run_id. Got {run_id_list=}")

        filter = {
            'run_id': {"$in": run_id_list},
            # 'metric': cls.metric_mapper[metric_name],
            'sim_clock': ts_range
        }
        projection = {
            "_id": 0,
            "sim_clock": 1,
            f"online_params.{cls.metric_mapper[metric_name]}": 1,
        }
        sort = list({
            'sim_clock': 1,
        }.items())

        cursor = kpi_collection.find(filter,
                        projection=projection,
                        sort=sort)

        df = pd.DataFrame(list(cursor))
        df = pd.concat([df.drop(['online_params'], axis=1), df['online_params'].apply(pd.Series)], axis=1)
        df = df.set_index('sim_clock', drop=True)

        result = dataframe_to_response(metric_name, cls.apply_formula(df, cls.metric_mapper[metric_name], formula))

        # df['metric'] = cls.metric_mapper[metric_name]
        # result = dataframe_to_json_table(metric_name, cls.apply_formula(df, cls.metric_mapper[metric_name], formula))

        return result

    @classmethod
    def get_static_metric_as_is(cls, run_id_list, metric_name, ts_range, payload):
        ''''''
        db = app.data.driver.db
        kpi_collection = db['engine']
        formula = payload.get('formula')

        if len(run_id_list) != 1:
            raise Exception(f"This query only accepts 1 value for run_id. Got {run_id_list=}")

        filter = {
            'run_id': {"$in": run_id_list},
            'sim_clock': ts_range
        }
        projection = {
            "_id": 0,
            "sim_clock": 1,
            f"online_params.{cls.metric_mapper[metric_name]}": 1,
        }
        sort = list({
            'sim_clock': 1,
        }.items())

        cursor = kpi_collection.find(filter,
                        projection=projection,
                        sort=sort)

        # df = pd.DataFrame(list(cursor)) \
        #         .set_index('sim_clock', drop=True) \
        #         .rename(columns={'value': metric_name})
        # df[metric_name] = df[metric_name].cumsum()

        # filter['metric'] = 'num_served'
        # cursor = kpi_collection.find(filter,
        #                 projection=projection,
        #                 sort=sort)

        # served_df = pd.DataFrame(list(cursor)) \
        #         .set_index('sim_clock', drop=True)
        # served_df['value'] = served_df['value'].cumsum()

        # df[metric_name] = df[metric_name]/served_df['value']

        # result = dataframe_to_response(metric_name, cls.apply_formula(df, metric_name, formula))

        # return result
        return []



    @classmethod
    def apply_formula(cls, df, column, formula):

        # Formula is a tuple wih as many intries in asequence as needed for instance
        # ("cumulative")
        # ("rolling", window, "mean")
        # ("rolling", window, "sum") etc...
        # There must be a better way to do this..
        # Explore possibility
        # -- Library to convert instructions to pandas functionality (ideal)
        # -- Avoid Pandas (also great if the computation can be duplicated easily)
        # -- precompute all metrics - memory intensive
        # -- Using TSDB like prometheus etc. (additional layer of complexity)
        #
        # print(column, formula)
        if formula is not None:
            # if formula.get('type') == 'cumulative':
            if formula[0] == 'cumulative':
                df[column] = df[column].cumsum()

            # if formula.get('type') == 'rolling':
            elif formula[0] == 'rolling':
                # window = formula.get('window', 10)
                # fn = formula.get('fn', 'mean')
                window = formula[1]
                fn = formula[2]
                if fn == 'mean':
                    df[column] = df[column].rolling(window).mean()
                    df.dropna(inplace=True)
                    # print(df.head(20))
                if fn == 'sum':
                    df[column] = df[column].rolling(window).sum()
                    df.dropna(inplace=True)

        return df
