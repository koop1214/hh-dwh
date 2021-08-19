import luigi
from dateutil.relativedelta import relativedelta

class DbConfig(luigi.Config):
    conn_string = luigi.OptionalParameter(default=None)

    host = luigi.Parameter(default='localhost')

    port = luigi.IntParameter(default=5432)

    user = luigi.Parameter(default='luigi')

    password = luigi.OptionalParameter(default=None)

    database = luigi.Parameter(default='luigi_demo')


class FactVacanciesRangeTask(luigi.WrapperTask):
    start = luigi.DateParameter()
    stop = luigi.DateParameter()

    def requires(self):
        from tasks.fact import FactVacanciesTask

        current_day = self.start
        while current_day <= self.stop:
            yield FactVacanciesTask(date=current_day)
            current_day += relativedelta(days=1)
