import os
import pandas as pd
import time
import cbk_data
import fred_data
from pathlib import Path
from fredapi import Fred


def main_cbk(
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
        print(f"running loop for variable: {k}")
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
    outpath = Path("raw_cbk" + time.strftime("%d_%m_%Y") + ".csv")
    with outpath as e:
        data2save.to_csv(e, index=False)


def main_fred(
    code_vars: dict = None, start_time="01/01/1980", end_time=time.strftime("%d/%m/%Y")
):
    ### checking code_vars variable
    if code_vars is None:
        code_vars = {
            "crude_oil_wti": "DCOILWTICO",
            "crude_oil_brent": "DCOILBRENTEU",
            "gas_henry_hub": "DHHNGSP",
            "nominal_broad_usdollar": "DTWEXBGS",
            "yuan_dollar_spot_tc": "DEXCHUS",
            "usdollar_euro": "DEXUSEU",
            "treasury3month": "DTB3",
            "treasury1year": "DTB1YR",
            "treasury4week": "DTB4WK",
            "treasury6month": "DTB6",
            "chn_x": "XTEXVA01CNM667S",
            "chn_m": "XTIMVA01CNM667S",
            "ue_x": "XTEXVA01EZM667S",
            "ue_m": "XTIMVA01EZM667S",
            "usa_x": "BOPTEXP",
            "usa_m": "BOPTIMP",
        }
    else:
        if isinstance(code_vars, dict):
            print("Using a custom code_vars dictionary")
        else:
            raise Exception("The parameter code_vars is not a dictionary")
    ### access to fred API
    fred = Fred(os.getenv("API_FED"))

    ### getting the data
    data_fred = {}
    for k, v in codes_vars.items():
        print(f"getting the variable: {k}")
        data_fred[k] = fred.get_series(v)

    ## doing the call
    data_fred_clean = {}
    for k, v in codes_vars.items():
        print(f"cleaning data for variable: {k}")
        data_fred_clean[k] = fred_data.cleaning_fred(ds=data_fred[k], var_name=k)

    ### saving as csv
    raw_fred = pd.concat(data_fred_clean, axis=0, ignore_index=True)
    outpath = Path("raw_fred" + time.strftime("%d_%m_%Y") + ".csv")
    with outpath as e:
        raw_fred.to_csv(e, index=False)


if __name__ == "__main__":
    main_cbk()
    main_fred()
