import requests
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET


class api_call:
    ## init params
    def __init__(
        self,
        start_date,
        end_date,
        var_code,
        type_exc,
        var_name,
        local_path="bccr.xml",
        url="https://gee.bccr.fi.cr/Indicadores/Suscripciones/WS/wsindicadoreseconomicos.asmx/ObtenerIndicadoresEconomicos?",
    ):
        self.start_date = start_date
        self.end_date = end_date
        self.var_code = var_code
        self.type_exc = type_exc
        self.var_name = var_name
        self.local_path = local_path
        self.url = url

    ## BCCR params
    def params_bccr(self):
        self.params_bccr = {
            "Indicador": self.var_code,
            "FechaInicio": self.start_date,
            "FechaFinal": self.end_date,
            "Nombre": "Ken",
            "Subniveles": "S",
            "CorreoElectronico": "kado2094@gmail.com",
            "Token": "22AEOAA2T3",
        }
        return self.params_bccr

    ## API call
    def api_call(self):
        ## call
        try:
            response = requests.get(self.url, params=self.params_bccr)
        except requests.exceptions.Timeout:
            print("time exeption error")
        ### Maybe set up for a retry, or continue in a retry loop
        except requests.exceptions.TooManyRedirects:
            print("bad url error")
        ### Tell the user their URL was bad and try a different one
        except requests.exceptions.RequestException as e:
            ## catastroph .
            print("catastrophic error")
            raise SystemExit(e)
        finally:
            ## xml text
            root = ET.ElementTree(ET.fromstring(response.content))
            ## saving xml
            root.write(self.local_path, encoding="UTF-8", xml_declaration=True)

    ## creating data
    def create_data(self):
        self.df = (
            pd.read_xml(
                self.local_path,
                xpath=".//Datos_de_INGC011_CAT_INDICADORECONOMIC//INGC011_CAT_INDICADORECONOMIC",
                namespaces={"ns0": "http://ws.sdde.bccr.fi.cr"},
            )
            .rename(
                columns={
                    "COD_INDICADORINTERNO": "cod",
                    "DES_FECHA": "date",
                    "NUM_VALOR": "value",
                }
            )
            .loc[:, ["cod", "date", "value"]]
        )
        # self.root_parse = ET.parse(self.local_path)
        # self.rows = {
        #     "cod": [x.text for x in self.root_parse.findall(".//COD_INDICADORINTERNO")],
        #     "date": [x.text for x in self.root_parse.findall(".//DES_FECHA")],
        #     "value": [x.text for x in self.root_parse.findall(".//NUM_VALOR")],
        # }
        # self.df = pd.DataFrame(self.rows)
        self.df.loc[:, "var"] = self.var_name
        self.df.loc[:, "type"] = self.type_exc
        return self.df


def xm_notacc(df):
    """
    Fun to convert the data to not accumulative by year-month
    """
    df.loc[:, "value_lag"] = df.groupby("year")["value"].shift()
    df.loc[:, "value_lag"] = df.loc[:, "value_lag"].replace({np.nan: 0})
    df.loc[:, "valnotacc"] = df.loc[:, "value"] - df.loc[:, "value_lag"]
    df = (df.drop(["value_lag", "value"], axis=1)
            .rename(columns={"valnotacc"  : "value"}))
    return df