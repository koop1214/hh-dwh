import abc
import logging
from contextlib import contextmanager

import luigi
import sqlalchemy
from luigi.contrib.sqla import CopyToTable
from luigi.contrib.sqla import SQLAlchemyTarget
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import Insert


class SQLAlchemyWithRows(SQLAlchemyTarget):
    rows = None

    def __init__(self, connection_string, target_table, update_id, echo=False, connect_args=None, rows=None):
        super(SQLAlchemyWithRows, self).__init__(connection_string, target_table, update_id, echo, connect_args)
        self.rows = rows

    @contextmanager
    def open(self, mode):
        yield self.rows

    def exists(self):
        return self.rows is not None


class SQLAlchemyQuery(luigi.Task):
    _logger = logging.getLogger('luigi-interface')

    echo = False
    connect_args = {}
    rows = None

    @property
    @abc.abstractmethod
    def connection_string(self):
        return None

    @property
    @abc.abstractmethod
    def table(self):
        return None

    @property
    @abc.abstractmethod
    def query(self):
        return None

    @property
    def update_id(self):
        return self.task_id

    def run(self):
        output = self.output()
        engine = output.engine

        self._logger.info('Executing query: {query}'.format(query=self.query))

        with engine.begin() as conn:
            rs = conn.execute(self.query)

            self.rows = rs.fetchall()

    def output(self):
        return SQLAlchemyWithRows(
            connection_string=self.connection_string,
            target_table=self.table,
            update_id=self.update_id,
            connect_args=self.connect_args,
            echo=self.echo,
            rows=self.rows)


@compiles(Insert)
def append_string(insert, compiler, **kw):
    s = compiler.visit_insert(insert, **kw)
    if 'append_string' in insert.kwargs:
        return s + " " + insert.kwargs['append_string']
    return s


class SkipOrCopyToTable(CopyToTable):
    @property
    @abc.abstractmethod
    def unique_key(self) -> str or None:
        return None

    def copy(self, conn, ins_rows, table_bound: sqlalchemy.schema.Table):
        table_bound.implicit_returning = False
        columns = [sqlalchemy.Column(*c[0], **c[1]) for c in self.columns] if len(
            self.columns) > 0 else table_bound.columns

        bound_cols = dict((c, sqlalchemy.bindparam("_" + c.key)) for c in columns)
        ins = table_bound.insert(append_string=f'ON CONFLICT ({self.unique_key}) DO NOTHING').values(bound_cols)

        conn.execute(ins, ins_rows)
