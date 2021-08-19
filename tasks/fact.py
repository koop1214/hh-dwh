import datetime
from abc import ABC

import luigi
import numpy as np
import pandas as pd

from tasks.aux import DbConfig
from tasks.dim import DimTypesTask, DimAreasTask, DimEmployersTask, DimSchedulesTask, ExchangeRatesTask
from tasks.download import DownLoadVacanciesTask
from tasks.sqla import SQLAlchemyQuery, SkipOrCopyToTable


class ListTask(SQLAlchemyQuery, ABC):
    date = luigi.DateParameter(default=datetime.date.today())

    __db_config = DbConfig()
    connection_string = __db_config.conn_string


class ListTypesTask(ListTask):
    table = 'dim_types'
    query = 'SELECT id AS type_id, code AS type_code FROM dim_types ORDER BY id;'

    def requires(self):
        return DimTypesTask(self.date)


class ListSchedulesTask(ListTask):
    table = 'dim_schedules'
    query = 'SELECT id AS schedule_id, code AS schedule_code FROM dim_schedules ORDER BY id;'

    def requires(self):
        return DimSchedulesTask(self.date)


class ListAreasTask(ListTask):
    table = 'dim_areas'
    query = 'SELECT id AS area_id, code AS area_code FROM dim_areas ORDER BY id;'

    def requires(self):
        return DimAreasTask(self.date)


class ListEmployersTask(ListTask):
    table = 'dim_employers'
    query = 'SELECT id AS employer_id, code AS employer_code FROM dim_employers ORDER BY id;'

    def requires(self):
        return DimEmployersTask(self.date)


class ListGradesTask(SQLAlchemyQuery):
    __db_config = DbConfig()
    connection_string = __db_config.conn_string
    table = 'dim_grades'
    query = 'SELECT id AS grade_id, aliases AS grade_aliases FROM dim_grades WHERE id > 0 ORDER BY id;'


class ListExchangeRatesTask(ListTask):
    table = 'exchange_rates'

    def requires(self):
        return ExchangeRatesTask(self.date)

    @property
    def query(self):
        return f'SELECT currency, rate FROM exchange_rates WHERE date=\'{self.date}\''


class FactVacanciesTask(SkipOrCopyToTable):
    date = luigi.DateParameter(default=datetime.date.today())

    __db_config = DbConfig()
    connection_string = __db_config.conn_string
    reflect = True

    table = 'fact_vacancies'
    unique_key = 'id'

    def requires(self):
        return {
            'vacancies': DownLoadVacanciesTask(self.date),
            'types': ListTypesTask(self.date),
            'schedules': ListSchedulesTask(self.date),
            'areas': ListAreasTask(self.date),
            'employers': ListEmployersTask(self.date),
            'grades': ListGradesTask(),
            'rates': ListExchangeRatesTask(self.date),
        }

    def rows(self):
        types_df = self.__get_df('types')
        schedules_df = self.__get_df('schedules')
        areas_df = self.__get_df('areas')
        employers_df = self.__get_df('employers')
        rates_df = self.__get_df('rates').append({'currency': 'RUR', 'rate': 1.}, ignore_index=True)
        grades = {row.grade_id: [a.lower() for a in row.grade_aliases.split(',')] for row in self.input()['grades'].rows}

        def find_grade_id(name: str) -> int:
            name = name.lower()

            for key, values in grades.items():
                for value in values:
                    if value in name:
                        return key

            return 0

        def get_net_salary(salary, gross, rate):
            if pd.isnull(salary):
                return salary

            res = salary * rate * 87 / 100 if gross else salary * rate
            return round(res)

        with self.input()['vacancies'].open('r') as r_file:
            df = pd.read_csv(r_file, sep=';', parse_dates=['created_at'],
                             dtype={'area_code': str, 'employer_code': str,  'salary_currency': str, 'salary_from': 'Int64', 'salary_to': 'Int64'},
                             converters = {'salary_gross': lambda x: bool(int(x))})

            df = df.merge(types_df, on='type_code')
            df = df.merge(schedules_df, on='schedule_code')
            df = df.merge(areas_df, on='area_code')
            df = df.merge(employers_df, on='employer_code')
            df = df.merge(rates_df, how='left', left_on='salary_currency', right_on='currency')

            df['created_date_id'] = df['created_at'].dt.strftime('%Y%m%d')
            df['grade_id'] = df['name'].apply(find_grade_id)
            df['salary_from'] = df.apply(lambda x: get_net_salary(x['salary_from'], x['salary_gross'], x['rate']), axis=1)
            df['salary_to'] = df.apply(lambda x: get_net_salary(x['salary_to'], x['salary_gross'], x['rate']), axis=1)
            df['salary_from'] = df['salary_from'].astype('Int64')
            df['salary_to'] = df['salary_to'].astype('Int64')

            columns = self.table_bound.columns
            column_keys = columns.keys()
            df = df.replace({np.NaN: None})
            rows = df[column_keys].to_dict(orient='split')['data']
            return rows

    def __get_df(self, input_key: str) -> pd.DataFrame:
        rows = self.input()[input_key].rows
        values = [row.values() for row in rows]
        columns = list(rows[0].keys())
        df = pd.DataFrame(values, columns=columns)

        return df
