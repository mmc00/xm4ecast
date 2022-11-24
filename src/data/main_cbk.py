import requests
import os
import pandas as pd
import numpy as np
import time
import sys
import cbk_data
from pathlib import Path


def main(
    url: str = "https://gee.bccr.fi.cr/Indicadores/Suscripciones/WS/wsindicadoreseconomicos.asmx/ObtenerIndicadoresEconomicos?",
    start_time="01/01/1980",
    end_time=time.strftime("%d/%m/%Y"),
    params_bccr: dict = None,
    code_vars: dict = None,
):
    """
    The params neccesaries are:
    params_bccr: These are the inputs for the auth of BCCR's API. Usually the user, token and the password.
    code_vars: These is a dictionary the variable name and it's code (from BCCR table).

    """

    ## Checking the params_bccr dictionary
    if params_bccr is None:
        params_bccr = {
            "Nombre": "Marlon",
            "Subniveles": "S",
            "CorreoElectronico": os.getenv("BCCR_USER"),
            "Token": os.getenv("BCCR_PASS"),
        }
    else:
        if isinstance(params_bccr, dict):
            print("Using a custom params_bccr dictionary")
        else:
            raise Exception("The parameter params_bccr is not a dictionary")

    ### checking the code_vars dictionary
    if code_vars is None:
        code_vars = {
            "exp": "1992",
            "imp": "1993",
            "imae": "87703",
            "tpm": "3541",
            "monex_amount_mean": "3451",
            "tc_monex": "3438",
            "gold": "1979",
            "tc_sell": "3140",
            "tc_buy": "3280",
            "mil_count": "3799",
        }
    else:
        if isinstance(code_vars, dict):
            print("Using a custom code_vars dictionary")
        else:
            raise Exception("The parameter code_vars is not a dictionary")

    ### running the code for each variable
    api_varscall = {}
    for k, v in code_vars.items():
        api_varscall[k] = cbk_data.api_call(
            var_code=v,
            start_date=start_time,
            end_date=end_time,
            type_exc="",
            var_name=k,
        )
        api_varscall[k].params_bccr()
        api_varscall[k].api_call()
        api_varscall[k] = api_varscall[k].create_data()
        api_varscall[k] = (
            api_varscall[k].drop(columns="type").rename(columns={"bank": "variable"})
        )

    ### cleaning for IMAE variable
    api_varscall["imae"] = api_varscall["imae"].query("cod == 87703")

    ### saving as CSV
    data2save = pd.concat(api_varscall, ignore_index=True)
    outpath = Path("raw_cbk.csv")
    with outpath as e:
        data2save.to_csv(e, index=False)


if __name__ == "__main__":
    main()
