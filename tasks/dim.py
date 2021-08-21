import abc
import datetime
import locale
from typing import List

import luigi
import pandas as pd
import sqlalchemy

from tasks.aux import DbConfig
from tasks.download import DownLoadVacanciesTask, DownLoadExchangeRatesTask
from tasks.sqla import SkipOrCopyToTable


class DimTask(SkipOrCopyToTable):
    """
    An abstract task for insert or skip dim tables.

    Usage:

        Subclass and override the following attributes:

        * `columns`,
        * `table`,
        * `unique_key`,
        * `input_columns`
    """
    date = luigi.DateParameter(default=datetime.date.today())

    __db_config = DbConfig()
    connection_string = __db_config.conn_string
    reflect = False

    @property
    @abc.abstractmethod
    def input_columns(self) -> List:
        return []

    def rows(self):
        with self.input().open() as csv_file:
            df = pd.read_csv(csv_file, sep=';')
            df = df[self.input_columns].drop_duplicates()
            rows = df.to_dict(orient='split')['data']
            return rows

    def requires(self):
        return DownLoadVacanciesTask(self.date)


class DimAreasTask(DimTask):
    table = 'dim_areas'
    unique_key = 'code'
    columns = [
        (['code', sqlalchemy.String()], {}),
        (['name', sqlalchemy.String()], {}),
    ]
    input_columns = ['area_code', 'area_code', 'area_name']


class DimTypesTask(DimTask):
    table = 'dim_types'
    unique_key = 'code'
    columns = [
        (['code', sqlalchemy.String()], {}),
        (['name', sqlalchemy.String()], {}),
    ]
    input_columns = ['type_code', 'type_code', 'type_name']


class DimSchedulesTask(DimTask):
    table = 'dim_schedules'
    unique_key = 'code'
    columns = [
        (['code', sqlalchemy.String()], {}),
        (['name', sqlalchemy.String()], {}),
    ]
    input_columns = ['schedule_code', 'schedule_code', 'schedule_name']


class DimEmployersTask(DimTask):
    table = 'dim_employers'
    unique_key = 'code'
    columns = [
        (['code', sqlalchemy.String()], {}),
        (['name', sqlalchemy.String()], {}),
        (['trusted', sqlalchemy.Boolean()], {}),
    ]
    input_columns = ['employer_code', 'employer_code', 'employer_name', 'employer_trusted']


class ExchangeRatesTask(SkipOrCopyToTable):
    date = luigi.DateParameter(default=datetime.date.today())

    __db_config = DbConfig()
    connection_string = __db_config.conn_string
    reflect = True
    unique_key = 'date,currency'
    table = 'exchange_rates'

    def rows(self):
        with self.input().open() as xml_file:
            df = pd.read_xml(xml_file, encoding='windows-1251')
            df.rename(columns={'CharCode': 'currency'}, inplace=True)
            df['date'] = self.date
            df['rate'] = df['Value'].str.replace(',', '.').astype(float)
            df['rate'] = df['rate'] / df['Nominal']

            columns = self.table_bound.columns
            column_keys = columns.keys()
            rows = df[column_keys].to_dict(orient='split')['data']
            return rows

    def requires(self):
        return DownLoadExchangeRatesTask(self.date)
