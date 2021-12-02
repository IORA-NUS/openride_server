

def infer_run_id_list(scopedVars, payload):

    # print(f"{scopedVars = }")
    # print(f"{payload = }")

    try:
        run_id = scopedVars['run_id']['value']
    except Exception as e:
        # print(str(e))
        try:
            run_id = payload['run_id']
        except:
            run_id = None

    if  (isinstance(run_id, str)):
        return [run_id]
    elif (isinstance(run_id, list)): # and (len(run_id) == 1):
        return run_id
    else:
        # raise Exception(f"This query only accepts 1 value for run_id. Got {run_id=}")
        raise Exception(f"Missing run_id in request")
