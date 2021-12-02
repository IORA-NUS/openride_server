
import pandas as pd
from flask import current_app as app
from analytics.utils.grafana_pandas_datasource.util import dataframe_to_response, dataframe_to_json_table, annotations_to_response


class TripFactory():


    @classmethod
    def get_passenger_trip_pickup_location(cls, run_id_list, metric_name, ts_range, payload):
        ''' '''
        db = app.data.driver.db
        waypoint_collection = db['waypoint']

        if len(run_id_list) != 1:
            raise Exception(f"This query only accepts 1 value for run_id. Got {run_id_list=}")


        filter = {
            'run_id': {"$in": run_id_list},
            'sim_clock': ts_range,
            'event.state': 'passenger_requested_trip'
        }
        projection = {
            "_id": 0,
            "sim_clock": 1,
            "run_id": 1,
            "event.location.coordinates": 1,
            # "event.location": 1,
        }
        sort = list({
            'sim_clock': 1,
        }.items())

        cursor = waypoint_collection.find(filter,
                        projection=projection,
                        sort=sort)

        df = pd.DataFrame(list(cursor)) \
                .set_index('sim_clock', drop=True)
        # df['weight'] = 1
        df['latitude'] = [loc['location']['coordinates'][0] for loc in list(df['event'])]
        df['longitude'] = [loc['location']['coordinates'][1] for loc in list(df['event'])]
        # df['location'] = [loc['location'] for loc in list(df['event'])]

        df.drop(columns="event")

        result = dataframe_to_json_table(metric_name, df)

        return result



    @classmethod
    def get_passenger_trip_dropoff_location(cls, run_id_list, metric_name, ts_range, payload):
        ''' '''
        db = app.data.driver.db
        waypoint_collection = db['waypoint']

        if len(run_id_list) != 1:
            raise Exception(f"This query only accepts 1 value for run_id. Got {run_id_list=}")

        filter = {
            'run_id': {"$in": run_id_list},
            'sim_clock': ts_range,
            'event.state': 'passenger_completed_trip'
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

        result = dataframe_to_json_table(metric_name, df)

        return result



    @classmethod
    def get_driver_available_location(cls, run_id, metric_name, ts_range, payload):
        ''' '''

