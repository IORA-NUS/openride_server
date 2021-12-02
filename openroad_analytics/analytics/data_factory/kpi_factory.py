import pandas as pd
from flask import current_app as app
from analytics.utils.grafana_pandas_datasource.util import dataframe_to_response, dataframe_to_json_table, annotations_to_response


class KPIFactory():

    metric_mapper = {
        'revenue' : 'revenue',
        'num_served' : 'num_served',
        'num_cancelled' : 'num_cancelled',
        'wait_time_pickup' : 'wait_time_pickup',
        'wait_time_driver_confirm' : 'wait_time_driver_confirm',
        'wait_time_total' : 'wait_time_total',
        'wait_time_assignment' : 'wait_time_assignment',
        'service_score' : 'service_score',

        'revenue_per_trip' : 'revenue',
        'num_served_per_trip' : 'num_served',
        'num_cancelled_per_trip' : 'num_cancelled',
        'wait_time_pickup_per_trip' : 'wait_time_pickup',
        'wait_time_driver_confirm_per_trip' : 'wait_time_driver_confirm',
        'wait_time_total_per_trip' : 'wait_time_total',
        'wait_time_assignment_per_trip' : 'wait_time_assignment',
        'service_score_per_trip' : 'service_score',
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
        ''''''
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
        # df2 = df.rename(columns={
        #             "run_id": "value",
        #             "name": "text"
        #         })

        # print(dataframe_to_json_table('test', df2))

        # print(df)
        return df


    @classmethod
    def get_metric(cls, run_id_list, metric_name, ts_range, payload):
        ''''''
        # db = app.data.driver.db
        # kpi_collection = db['kpi']
        # formula = payload.get('formula')

        # if payload.get('compare', False):
        if len(run_id_list) > 1:
            return cls.get_metric_cmp(run_id_list, metric_name, ts_range, payload)
        else:
            return cls.get_metric_as_is(run_id_list, metric_name, ts_range, payload)


        # if len(run_id_list) != 1:
        #     raise Exception(f"This query only accepts 1 value for run_id. Got {run_id_list=}")

        # filter = {
        #     'run_id': {"$in": run_id_list},
        #     'metric': cls.metric_mapper[metric_name],
        #     'sim_clock': ts_range
        # }
        # projection = {
        #     "_id": 0,
        #     "sim_clock": 1,
        #     "value": 1,
        # }
        # sort = list({
        #     'sim_clock': 1,
        # }.items())

        # cursor = kpi_collection.find(filter,
        #                 projection=projection,
        #                 sort=sort)

        # df = pd.DataFrame(list(cursor)) \
        #         .set_index('sim_clock', drop=True) \
        #         .rename(columns={'value': metric_name})

        # result = dataframe_to_response(metric_name, cls.apply_formula(df, metric_name, formula))

        # return result

    @classmethod
    def get_metric_rate(cls, run_id_list, metric_name, ts_range, payload):
        ''''''
        # if payload.get('compare', False):
        if len(run_id_list) > 1:
            return cls.get_metric_rate_cmp(run_id_list, metric_name, ts_range, payload)
        else:
            return cls.get_metric_rate_as_is(run_id_list, metric_name, ts_range, payload)


    @classmethod
    def get_metric_as_is(cls, run_id_list, metric_name, ts_range, payload):
        ''''''
        db = app.data.driver.db
        kpi_collection = db['kpi']
        formula = payload.get('formula')

        if len(run_id_list) != 1:
            raise Exception(f"This query only accepts 1 value for run_id. Got {run_id_list=}")

        filter = {
            'run_id': {"$in": run_id_list},
            'metric': cls.metric_mapper[metric_name],
            'sim_clock': ts_range
        }
        projection = {
            "_id": 0,
            "sim_clock": 1,
            "value": 1,
        }
        sort = list({
            'sim_clock': 1,
        }.items())

        cursor = kpi_collection.find(filter,
                        projection=projection,
                        sort=sort)

        df = pd.DataFrame(list(cursor)) \
                .set_index('sim_clock', drop=True) \
                .rename(columns={'value': metric_name})

        # result = dataframe_to_response(metric_name, cls.apply_formula(df, metric_name, formula))
        df = cls.apply_formula(df, metric_name, formula)
        result = dataframe_to_response(metric_name, df)

        return result

    @classmethod
    def get_metric_cmp(cls, run_id_list, metric_name, ts_range, payload):
        ''''''
        db = app.data.driver.db
        kpi_collection = db['kpi']
        formula = payload.get('formula')

        filter = {
            'run_id': {"$in": run_id_list},
            'metric': cls.metric_mapper[metric_name],
            'sim_clock': ts_range
        }
        projection = {
            "_id": 0,
            "sim_clock": 1,
            "run_id": 1,
            "value": 1,
        }
        sort = list({
            'sim_clock': 1,
            "run_id": 1,
        }.items())

        cursor = kpi_collection.find(filter,
                        projection=projection,
                        sort=sort)

        df = pd.DataFrame(list(cursor))
        df = pd.pivot_table(df,
                            index='sim_clock',
                            columns='run_id',
                            values='value')

        # result = dataframe_to_response(metric_name, cls.apply_formula(df, run_id_list, formula))
        df = cls.apply_formula(df, run_id_list, formula)
        result = dataframe_to_response(metric_name, df.rename(columns=cls.run_id_mappers))

        return result


    @classmethod
    def get_metric_rate_as_is(cls, run_id_list, metric_name, ts_range, payload):
        ''''''
        db = app.data.driver.db
        kpi_collection = db['kpi']
        formula = payload.get('formula')

        if len(run_id_list) != 1:
            raise Exception(f"This query only accepts 1 value for run_id. Got {run_id_list=}")

        filter = {
            'run_id': {"$in": run_id_list},
            'metric': cls.metric_mapper[metric_name],
            'sim_clock': ts_range
        }
        projection = {
            "_id": 0,
            "sim_clock": 1,
            "value": 1,
        }
        sort = list({
            'sim_clock': 1,
        }.items())

        cursor = kpi_collection.find(filter,
                        projection=projection,
                        sort=sort)

        df = pd.DataFrame(list(cursor)) \
                .set_index('sim_clock', drop=True) \
                .rename(columns={'value': metric_name})
        df[metric_name] = df[metric_name].cumsum()

        filter['metric'] = 'num_served'
        cursor = kpi_collection.find(filter,
                        projection=projection,
                        sort=sort)

        served_df = pd.DataFrame(list(cursor)) \
                .set_index('sim_clock', drop=True)
        served_df['value'] = served_df['value'].cumsum()

        df[metric_name] = df[metric_name]/served_df['value']

        # result = dataframe_to_response(metric_name, cls.apply_formula(df, metric_name, formula))
        df = cls.apply_formula(df, metric_name, formula)
        result = dataframe_to_response(metric_name, df)

        return result


    @classmethod
    def get_metric_rate_cmp(cls, run_id_list, metric_name, ts_range, payload):
        ''''''
        db = app.data.driver.db
        kpi_collection = db['kpi']
        formula = payload.get('formula')

        filter = {
            'run_id': {"$in": run_id_list},
            'metric': cls.metric_mapper[metric_name],
            'sim_clock': ts_range
        }
        projection = {
            "_id": 0,
            "sim_clock": 1,
            "run_id": 1,
            "value": 1,
        }
        sort = list({
            'sim_clock': 1,
            "run_id": 1,
        }.items())

        cursor = kpi_collection.find(filter,
                        projection=projection,
                        sort=sort)

        df = pd.DataFrame(list(cursor))
        df = pd.pivot_table(df,
                            index='sim_clock',
                            columns='run_id',
                            values='value')
        df[run_id_list] = df[run_id_list].cumsum()

        filter['metric'] = 'num_served'
        cursor = kpi_collection.find(filter,
                        projection=projection,
                        sort=sort)

        served_df = pd.DataFrame(list(cursor))
        served_df = pd.pivot_table(served_df,
                            index='sim_clock',
                            columns='run_id',
                            values='value')
        served_df[run_id_list] = served_df[run_id_list].cumsum()

        df = df/served_df

        # result = dataframe_to_response(metric_name, cls.apply_formula(df, run_id_list, formula))
        df = cls.apply_formula(df, run_id_list, formula)
        result = dataframe_to_response(metric_name, df.rename(columns=cls.run_id_mappers))

        return result




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
