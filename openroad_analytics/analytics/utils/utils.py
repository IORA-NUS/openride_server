

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

def apply_transform(df, column, transform):

    # Formula is a tuple wih as many intries in asequence as needed for instance
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
    if transform is not None:
        if transform[0] == 'rolling':
            # window = formula.get('window', 10)
            # fn = formula.get('fn', 'mean')
            window = transform[1]
            fn = transform[2]
            if fn == 'mean':
                df[column] = df[column].rolling(window).mean()
                df.dropna(inplace=True)
                # print(df.head(20))
            if fn == 'sum':
                df[column] = df[column].rolling(window).sum()
                df.dropna(inplace=True)
        else:
            raise Exception(f'Transform {transform[0]} is not supported')

    return df

