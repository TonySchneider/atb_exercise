#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__licence__ = 'GPL'
__version__ = '0.0.1'
__author__ = 'Tony Schneider'
__email__ = 'tonysch05@gmail.com'


import json
import os.path
import sys
import logging
import requests
import itertools
import pandas as pd
from typing import Union
from datetime import date
from shutil import copyfile

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-10s | %(message)s', stream=sys.stdout)

XLSX_FILE_PATH = "CarsData.xlsx"


def write_new_sheet(data: dict, fields: list, file_path: str) -> bool:
    """
    This method writes an old sheet and the new provided data.
    Sheets: ['Sheet1', 'calculated_perms'] -> df1, df2
    """
    status = True
    try:
        df1 = pd.read_excel(file_path, sheet_name='Sheet1')
        df2 = pd.DataFrame(data, columns=fields)

        writer = pd.ExcelWriter(path=file_path, engine='xlsxwriter')
        df1.to_excel(writer, index=False, header=True, sheet_name='Sheet1')
        df2.to_excel(writer, index=False, header=True, sheet_name='calculated_perms')
        writer.save()
    except Exception as e:
        logging.error(f"Didn't manage to write the new sheet. Error - '{e}'")
        status = False

    return status


def get_current_exchange_rate(currency: str, rate: str) -> Union[None, float]:
    """
    This method returns the exchange rate by the provided currency and rate.
    """
    coinbase_url = f'https://api.coinbase.com/v2/exchange-rates?currency={currency}'
    exchange_rate = None

    try:
        response = requests.get(url=coinbase_url)
        parsed_content = json.loads(response.content)
        exchange_rate = float(parsed_content['data']['rates'][rate])
    except ConnectionError as e:
        logging.error(f"Didn't manage to reach '{coinbase_url}' | Error - '{e}'")
    except KeyError:
        logging.error(f"Wrong coinbase JSON structure | url - '{coinbase_url}'")
    except Exception as e:
        logging.error(f"Didn't manage to get & parse the coinbase data | Error - '{e}'")

    return exchange_rate


def add_calculated_price(data: dict, rate_exchange: float) -> None:
    """
    This method calculates the price by <KM> * <(dt_today - dt_models_year).days> * <rate> format and inserts it to a new key.
    """
    data['Price'] = int(data['Q2-KM']) * (date.today() - date(day=1, month=1, year=data['Q5-ModelData']['year'])).days * rate_exchange


def eval_conditions(data: dict, conditions: dict) -> None:
    """
    This method evaluate the conditions and change the value to 'None' accordingly.
    """
    for key, condition in conditions.items():
        formatted_condition = None
        for data_key in data:
            if data_key in condition:
                formatted_condition = condition.replace(data_key, data[data_key])

        if eval(formatted_condition):
            data[key] = None


def get_permutations(data: dict, conditions: dict, rate_exchange: float):
    """
    This method generates a iterable variable that includes all the permutations.
    """
    keys = data.keys()
    values = data.values()

    for instance in itertools.product(*values):
        current_dict = dict(zip(keys, instance))
        eval_conditions(current_dict, conditions)
        add_calculated_price(current_dict, rate_exchange)

        yield current_dict


def load_n_parse_xlsx_data(file_path: str) -> dict:
    """
    This method loads the xlsx file, extracts the data and parses them to a new dictionary format.
    """
    iterable_data = None
    parsed_data = {'data': {}, 'conditions': {}}
    try:
        df = pd.read_excel(file_path, sheet_name='Sheet1').fillna('')
        iterable_data = list(df.T.to_dict().values())
        assert all(all(column in item.keys() for column in ['Property Name', 'Possible Values', 'Condition']) for item in iterable_data)
    except (TypeError, AssertionError):
        logging.error(f"Type error, check the xlsx data format.")
        iterable_data = None
    except Exception as e:
        logging.error(f"Didn't manage to open the provided file (path - '{file_path}') | Error - '{e}'.")

    for item in iterable_data:
        field = item['Property Name']
        splitted_data = item['Possible Values'].split(';')
        parsed_data['data'][field] = [json.loads(value) for value in splitted_data] if field == 'Q5-ModelData' else splitted_data
        if item['Condition']:
            parsed_data['conditions'][field] = item['Condition']

    return parsed_data


if __name__ == '__main__':
    logging.info("The client has been executed.")

    xlsx_data = load_n_parse_xlsx_data(XLSX_FILE_PATH)
    if not xlsx_data['data']:
        logging.error("No XLSX data, aborting...")
        sys.exit(1)

    usd_clp_exchange_rate = get_current_exchange_rate(currency='USD', rate='CLP')
    if not usd_clp_exchange_rate:
        logging.error("No exchange rate, aborting...")
        sys.exit(1)

    columns = list(xlsx_data['data'].keys()) + ['Price']
    calculated_perms = {column: [] for column in columns}
    for perm in get_permutations(xlsx_data['data'], xlsx_data['conditions'], usd_clp_exchange_rate):
        for column in columns:
            calculated_perms[column].append(perm[column])

    write_status = write_new_sheet(data=calculated_perms, fields=columns, file_path=XLSX_FILE_PATH)
    if not write_status:
        sys.exit(1)

    logging.debug("copying new sheet file to a volume folder")
    copyfile(XLSX_FILE_PATH, os.path.join('..', 'results', XLSX_FILE_PATH))

    logging.info("The client has been finished.")
