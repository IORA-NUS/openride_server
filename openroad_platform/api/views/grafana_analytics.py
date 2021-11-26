
# from http import HTTPStatus
# from flask import current_app as app
# from flask import abort, Response, jsonify, request
# from datetime import datetime, timezone
# from dateutil.parser import isoparse

# import json
# from flask_classful import FlaskView, route
# from eve.auth import requires_auth

# class GrafanaAnalyticsView(FlaskView):
#     ''' '''
#     route_prefix = 'analytics'
#     route_base = '/'
#     decorators = [requires_auth('kpi')]
#     db = None
#     allowed_metrics = {
#         'revenue_step': {
#             'collection': 'kpi',
#         },
#         'num_cancelled_step': {
#             'collection': 'kpi',
#         },
#         'num_served_step': {
#             'collection': 'kpi',
#         },
#         'wait_time_driver_confirm_step': {
#             'collection': 'kpi',
#         },
#         'wait_time_total_step': {
#             'collection': 'kpi',
#         },
#         'wait_time_assignment_step': {
#             'collection': 'kpi',
#         },
#         'wait_time_pickup_step': {
#             'collection': 'kpi',
#         },
#         'service_score_step': {
#             'collection': 'kpi',
#         },

#         'revenue_cum': {
#             'collection': 'kpi',
#         },
#         'num_cancelled_cum': {
#             'collection': 'kpi',
#         },
#         'num_served_cum': {
#             'collection': 'kpi',
#         },
#         'wait_time_driver_confirm_cum': {
#             'collection': 'kpi',
#         },
#         'wait_time_total_cum': {
#             'collection': 'kpi',
#         },
#         'wait_time_assignment_cum': {
#             'collection': 'kpi',
#         },
#         'wait_time_pickup_cum': {
#             'collection': 'kpi',
#         },
#         'service_score_cum': {
#             'collection': 'kpi',
#         },
#     }


#     def before_request(self, name, *args, **kwargs):
#         ''' '''
#         self.db = app.data.driver.db

#     @route('/', methods=['GET'])
#     def root(self, **lookup):
#         data = {
#             'status': 'ok'
#         }

#         return Response(json.dumps(data),
#                         status=HTTPStatus.OK,
#                         headers={'Content-Type': 'application/json'})

#     @route('/search', methods=['POST'])
#     def search(self, **lookup):
#         data = [k for k, _ in self.allowed_metrics.items()]

#         return Response(json.dumps(data),
#                         status=HTTPStatus.OK,
#                         headers={'Content-Type': 'application/json'})


#     @route('/query', methods=['POST'])
#     def query(self, **lookup):
#         ''' '''
#         # print(request.json)

#         data = []

#         # print(filter)
#         format = 'table'
#         run_id = request.json['scopedVars']['run_id']['value']

#         for target_def in request.json['targets']:
#             # format = target_def['type']

#             metric = target_def['target']
#             target_collection = self.allowed_metrics[metric]['collection']
#             collection = self.db[target_collection]

#             if target_collection == "kpi":
#                 # filter = lookup.copy()

#                 filter = {
#                     'run_id': run_id,
#                     'metric': metric,
#                     'sim_clock': {
#                         "$gte": isoparse(request.json['range']['from']),
#                         "$lt": isoparse(request.json['range']['to'])
#                     }
#                 }
#                 projection = {
#                     "_id": 0,
#                     "sim_clock": 1,
#                     "value": 1,
#                 }
#                 sort = list({
#                     'sim_clock': 1,
#                 }.items())


#                 cursor = collection.find(filter,
#                                 projection=projection,
#                                 sort=sort)

#                 cursor_data = list(cursor)
#                 if format == 'table':
#                     data.append({
#                         'columns': [
#                             {"text": metric, "type": "number"},
#                             {"text": "sim_clock", "type": "time"},
#                         ],
#                         "rows": [
#                             [doc['value'], doc['sim_clock'].timestamp()*1000]
#                                 for doc in cursor_data
#                         ]
#                     })
#                 else:
#                     data.append({
#                         'target': target_def['target'],
#                         'datapoints': [
#                             [doc['value'], doc['sim_clock'].timestamp()*1000]
#                                 for doc in cursor_data
#                         ]
#                     })

#         # print(json.dumps(data))


#         return Response(json.dumps(data),
#                         status=HTTPStatus.OK,
#                         headers={'Content-Type': 'application/json'})


# class GrafanaRunConfigView(FlaskView):
#     ''' '''
#     route_prefix = 'analytics/run_id'
#     route_base = '/'
#     decorators = [requires_auth('kpi')]
#     db = None

#     def before_request(self, name, *args, **kwargs):
#         ''' '''
#         self.db = app.data.driver.db

#     @route('/', methods=['GET'])
#     def root(self, **lookup):
#         data = {
#             'status': 'ok'
#         }

#         return Response(json.dumps(data),
#                         status=HTTPStatus.OK,
#                         headers={'Content-Type': 'application/json'})


#     @route('/search', methods=['POST'])
#     def run_config(self, **lookup):
#         data = []
#         collection = self.db['run_config']

#         filter = {
#         }
#         projection = {
#             "_id": 0,
#             "run_id": 1,
#             "name": 1,
#             "value": 1,
#         }
#         sort = list({
#             '_updated': -1,
#         }.items())

#         cursor = collection.find(filter,
#                         projection=projection,
#                         sort=sort)
#         cursor_data = list(cursor)

#         # data.append({
#         #     'columns': [
#         #         {"text": "run_id", "type": "string"},
#         #         {"text": "name", "type": "string"},
#         #     ],
#         #     "rows": [
#         #         [doc['run_id'], doc['name']]
#         #             for doc in cursor_data
#         #     ]
#         # })

#         data = [doc['run_id'] for doc in cursor_data]

#         return Response(json.dumps(data),
#                         status=HTTPStatus.OK,
#                         headers={'Content-Type': 'application/json'})


