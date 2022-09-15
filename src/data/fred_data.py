import pandas as pd

def cleaning_fred(ds, var_name):
    """
    Cleaning data series (ds)
    """
    dt = ds.to_frame().reset_index()
    dt = (dt.rename(columns={dt.columns[0] : "date",
                             dt.columns[1] : "value"})
            .assign(var = var_name)
         )
    return dt