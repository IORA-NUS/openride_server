
from http import HTTPStatus
from flask import current_app as app
from flask import abort, Response, jsonify, request
from datetime import datetime, timezone
from dateutil.parser import isoparse

import json
from flask_classful import FlaskView, route
from eve.auth import requires_auth

import pandas as pd

from analytics.utils.grafana_pandas_datasource.registry import data_generators as dg
from analytics.utils.grafana_pandas_datasource.util import dataframe_to_response, dataframe_to_json_table, annotations_to_response

from analytics.utils.utils import infer_run_id_list

class GrafanaView(FlaskView):
    ''' '''
    route_prefix = 'analytics'
    route_base = '/'
    # decorators = [requires_auth('kpi')]
    db = None

    def before_request(self, name, *args, **kwargs):
        ''' '''
        self.db = app.data.driver.db

    @route('/', methods=['GET'])
    def root(self, **lookup):
        data = {
            'status': 'ok'
        }

        return Response(json.dumps(data),
                        status=HTTPStatus.OK,
                        headers={'Content-Type': 'application/json'})

    @route('/search', methods=['GET', 'POST'])
    def search(self, **lookup):
        # print(request.headers, request.get_json())
        req = request.get_json()

        target = req.get('target', '*')

        if ':' in target:
            finder, target = target.split(':', 1)
        else:
            finder = target

        # print(f"{finder=}, {target=}, {dg.metric_readers=}, {dg.metric_finders=}")

        if not target or finder not in dg.metric_finders:
            metrics = []
            if target in ['*', '']:
                metrics += dg.metric_finders.keys()
                metrics += dg.metric_readers.keys()
            else:
                metrics.append(target)

            return jsonify(metrics)
        else:
            metric_options = dg.metric_finders[finder](target)

            print(list(metric_options[target]))

            return jsonify(list(metric_options[target]))


    @route('/query', methods=['GET', 'POST'])
    def query(self, **lookup):
        ''' '''
        # print(request.json)
        req = request.get_json()
        scopedVars = request.json['scopedVars']

        results = []

        ts_range = {'$gt': pd.Timestamp(req['range']['from']).to_pydatetime(),
                    '$lte': pd.Timestamp(req['range']['to']).to_pydatetime()}

        if 'intervalMs' in req:
            freq = str(req.get('intervalMs')) + 'ms'
        else:
            freq = None

        for target_def in req['targets']:
            # print(f"{target_def['payload'] = }")
            run_id_list = infer_run_id_list(scopedVars, target_def['payload'])

            # if type(target_def['payload']) == dict:
            #     formula = target_def['payload'].get('formula')
            # else:
            #     formula = None
            if type(target_def['payload']) == dict:
                payload = target_def['payload']
            else:
                payload = {}

            finder = target = target_def['target']
            query_results = dg.metric_readers[finder](run_id_list, target, ts_range, payload)

            # if req_type == 'table':
            #     results.extend(dataframe_to_json_table(target, query_results))
            # elif req_type == 'timeserie':
            #     results.extend(dataframe_to_response(target, query_results, freq=freq))
            # else:
            #     results.extend(dataframe_to_json_table(target, query_results))
            results.extend(query_results)

        return jsonify(results)


@route('/annotations', methods=['GET', 'POST'])
def query_annotations():
    # print(request.headers, request.get_json())
    req = request.get_json()

    results = []

    ts_range = {'$gt': pd.Timestamp(req['range']['from']).to_pydatetime(),
                '$lte': pd.Timestamp(req['range']['to']).to_pydatetime()}

    query = req['annotation']['query']

    finder = target = query
    results.extend(annotations_to_response(query, dg.annotation_readers[finder](target, ts_range)))

    return jsonify(results)


@route('/panels', methods=['GET', 'POST'])
def get_panel():
    # print(request.headers, request.get_json())
    req = request.args

    ts_range = {'$gt': pd.Timestamp(int(req['from']), unit='ms').to_pydatetime(),
                '$lte': pd.Timestamp(int(req['to']), unit='ms').to_pydatetime()}

    query = req['query']

    # if ':' not in query:
    #     abort(404, Exception('Target must be of type: <finder>:<metric_query>, got instead: ' + query))

    # finder, target = query.split(':', 1)
    finder = target = query

    return dg.panel_readers[finder](target, ts_range)
