import pandas as pd
from flask import current_app as app


class KPIFactory():


    @classmethod
    def get_run_id(cls, *args):
        ''''''
        db = app.data.driver.db
        run_config_collection = db['run_config']

        filter = {
        }
        projection = {
            "_id": 0,
            "run_id": 1, # Target should be part of teh df
            "name": 1,
            "value": 1,
        }
        sort = list({
            '_updated': -1,
        }.items())

        cursor = run_config_collection.find(filter,
                        projection=projection,
                        sort=sort)

        return pd.DataFrame(list(cursor))


    @classmethod
    def get_metric(cls, metric, ts_range, scopedVars, formula):
        ''''''
        db = app.data.driver.db
        kpi_collection = db['kpi']

        # print(f"{metric=}, {ts_range=}, {formula=}")
        run_id = scopedVars['run_id']['value']

        filter = {
            'run_id': run_id,
            'metric': metric,
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

        # cursor_data = list(cursor)
        df = pd.DataFrame(list(cursor)).set_index('sim_clock', drop=True)

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
        if formula is not None:
            # if formula.get('type') == 'cumulative':
            if formula[0] == 'cumulative':
                df['value'] = df['value'].cumsum()

            # if formula.get('type') == 'rolling':
            elif formula[0] == 'rolling':
                # window = formula.get('window', 10)
                # fn = formula.get('fn', 'mean')
                window = formula[1]
                fn = formula[2]
                if fn == 'mean':
                    df['value'] = df['value'].rolling(window).mean()
                    df.dropna(inplace=True)
                    # print(df.head(20))
                if fn == 'sum':
                    df['value'] = df['value'].rolling(window).sum()
                    df.dropna(inplace=True)


        return df
