import csv
import datetime
import os
from typing import Dict

import luigi
import requests
from luigi.format import TextFormat

from tasks.aux import DbConfig
from tasks.sqla import SQLAlchemyQuery


class ListSpecialitiesTask(SQLAlchemyQuery):
    __db_config = DbConfig()
    connection_string = __db_config.conn_string
    table = 'dim_specialities'
    query = 'SELECT * FROM dim_specialities ORDER BY id;'


class DownLoadVacanciesTask(luigi.Task):
    date = luigi.DateParameter(default=datetime.date.today())
    __db_config = DbConfig()

    @property
    def filename(self):
        return f'vacancies_{self.date}.csv'

    def requires(self):
        return ListSpecialitiesTask()

    def output(self):
        return luigi.LocalTarget(os.path.join('data', 'hh', self.filename))

    def run(self):
        self.output().makedirs()  # in case path does not exist

        with self.output().open(mode='w') as w_file:
            file_writer = csv.writer(w_file, delimiter=';', lineterminator='\n')
            file_writer.writerow(
                ['speciality_id',
                 'id',
                 'name',
                 'area_code',
                 'area_name',
                 'employer_code',
                 'employer_name',
                 'employer_trusted',
                 'type_code',
                 'type_name',
                 'schedule_code',
                 'schedule_name',
                 'premium',
                 'has_test',
                 'response_letter_required',
                 'salary_from',
                 'salary_to',
                 'salary_gross',
                 'salary_currency',
                 'created_at'])

            with self.input().open(mode='r') as rows:
                for speciality in rows:
                    search_text = self.__get_search_text(speciality['aliases'])

                    pages = 1
                    page = 0

                    while page < pages:
                        response = self.__download_dataset(str(self.date), page, search_text)
                        pages = response['pages']
                        print('search_text: ', search_text)
                        print('pages: ', pages)
                        print('found: ', response['found'])

                        for item in response['items']:
                            file_writer.writerow([speciality['id'],
                                                  item['id'],
                                                  item['name'],
                                                  item['area']['id'],
                                                  item['area']['name'],
                                                  item['employer']['id'] if item['employer'] and 'id' in item['employer'] else '0',
                                                  item['employer']['name'] if item['employer'] else '',
                                                  int(item['employer']['trusted']) if item['employer'] and 'trusted' in item['employer'] else 0,
                                                  item['type']['id'],
                                                  item['type']['name'],
                                                  item['schedule']['id'],
                                                  item['schedule']['name'],
                                                  int(item['premium']),
                                                  int(item['has_test']),
                                                  int(item['response_letter_required']),
                                                  item['salary']['from'] if item['salary'] else '',
                                                  item['salary']['to'] if item['salary'] else '',
                                                  int(item['salary']['gross']) if item['salary'] and item['salary']['gross'] is not None else 0,
                                                  item['salary']['currency'] if item['salary'] else '',
                                                  item['created_at']])

                        page += 1

    @staticmethod
    def __get_search_text(aliases: str) -> str:
        return ' OR '.join([f'"{alias}"' for alias in aliases.split(',')])

    @staticmethod
    def __download_dataset(date: str, page: int, search_text: str) -> Dict:
        response = requests.get('https://api.hh.ru/vacancies', params={
            'per_page': 100,
            'page': page,
            'area': 113,  # Россия
            'search_field': 'name',  # поиск только в заголовках
            'text': search_text,
            'date_from': date,
            'date_to': date
        })
        response.raise_for_status()

        return response.json()


class DownLoadExchangeRatesTask(luigi.Task):
    date = luigi.DateParameter(default=datetime.date.today())

    @property
    def filename(self):
        return f'rates_{self.date}.xml'

    def output(self):
        return luigi.LocalTarget(os.path.join('data', 'cbr', self.filename), format=luigi.format.NopFormat())

    def run(self):
        self.output().makedirs()  # in case path does not exist

        with self.output().open(mode='w') as w_file:
            response = self.__download_dataset(self.date)
            w_file.write(response)

    @staticmethod
    def __download_dataset(date: datetime.date):
        response = requests.get('http://www.cbr.ru/scripts/XML_daily.asp', params={
            'date_req': date.strftime('%d/%m/%Y')
        })
        response.raise_for_status()

        return response.content
