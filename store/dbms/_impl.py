import sqlite3

from store._data_files import DataFiles as _files
from ._exceptions import *
from ._custom_types import ColumnDefinitions as _ColumnDefinitions
from ._custom_types import ColumnTypes as _ColumnTypes
from ._custom_types import Row as _Row
import sqlite3 as _sql
from typing import Optional as _Optional
from os.path import exists as _exists


class _connect:

    def __init__(self):
        self._connection: _Optional[_sql.Connection] = None
        self._cursor: _Optional[_sql.Cursor] = None
        return

    def __enter__(self):
        self._connection = _sql.connect(_files.database)
        self._cursor = self._connection.cursor()
        return self._cursor

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._cursor.close()
        self._connection.commit()
        self._connection.close()
        return


def _validate_table_name(name: str) -> None:

    with _connect() as crs:
        # Verify a table with the given name exists in the database
        stmt = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{name}'"
        crs.execute(stmt)
        rows = crs.fetchall()
        if len(rows) == 0:
            raise TableDoesNotExist(name)  # _sql.OperationalError(f'no such table: {table_name}')

    return


def _validate_columns(table_name: str, column_definitions: _ColumnDefinitions) -> None:

    with _connect() as crs:
        # Fetch table_name's column definitions from the database
        crs.execute(f"pragma table_info('{table_name}');")
        rows = crs.fetchall()

    col_defs = {str(row[1]): str(row[2]).lower() for row in rows}

    # Assure the column info passed in matches table_name's columns in the database
    for name, typ in column_definitions.items():
        if name not in col_defs.keys():
            # Caller gave a column name not found in the database
            raise UndefinedColumnName(name)
        if not isinstance(typ, _ColumnTypes):  # if typ not in typ_map.keys():
            # Caller gave a type for this column that is not supported
            raise TypeError
        if col_defs[name] != typ.name.lower():
            # Caller gave a type for this column that doesn't match the database
            raise InvalidColumnType(col_name=name, typ=typ)

    return


def _validate_rows(table_name: str, column_definitions: _ColumnDefinitions, rows: _Row | list[_Row]) -> None:

    # If a single row is passed in, put it in a list as the logic
    # later in the function depends on "rows" being a list of _Row
    if isinstance(rows, _Row):
        rows = [rows]

    # Assure the data in the rows is of the correct type
    for row in rows:
        for j, col in enumerate(row):
            ct = list(column_definitions.values())
            ct = ct[j].name.lower()
            if ct == 'text':
                if col:
                    if not isinstance(col, str):
                        raise TypeError
            elif ct == 'integer':
                if col:
                    if not isinstance(col, int):
                        raise TypeError
            else:
                raise TypeError  # I don't think we should ever end in this case, but...


def create_database() -> None:

    if _exists(_files.database):
        raise FileExistsError(_files.database)

    with _connect() as crs:
        pass

    return


def create_table(name: str, column_definitions: _ColumnDefinitions) -> None:

    table_name = name.lower()

    columns = []
    for col_name, col_type in column_definitions.items():
        column = f'{col_name} {col_type.value}'
        if column_definitions.unique_column == col_name:
            column += ' NOT NULL UNIQUE'
        columns.append(column)
    columns = ', '.join(columns)

    stmt = f'CREATE TABLE {table_name} ({columns})'

    with _connect() as crs:
        crs.execute(stmt)

    return


def insert(table_name: str, column_definitions: _ColumnDefinitions, row: _Row) -> int:

    _validate_table_name(table_name)
    _validate_columns(table_name, column_definitions)
    _validate_rows(table_name, column_definitions, row)

    columns = ', '.join([c for c in column_definitions.keys()])
    values = ', '.join(['?'] * len(column_definitions))
    params = [v for v in row]
    stmt = f"INSERT INTO {table_name.lower()} ({columns}) VALUES ({values})"

    with _connect() as crs:
        try:
            crs.execute(stmt, params)
            rowid = crs.lastrowid
        except _sql.IntegrityError as e:
            raise IntegrityError(e)

    return rowid


def insert_many(table_name: str, column_definitions: _ColumnDefinitions, rows: list[_Row]) -> None:

    _validate_table_name(table_name)
    _validate_columns(table_name, column_definitions)

    columns = ', '.join([c for c in column_definitions.keys()])
    values = ', '.join(['?'] * len(column_definitions))
    params = [v for v in rows]
    stmt = f"INSERT INTO {table_name.lower()} ({columns}) VALUES ({values})"

    conn = _sql.connect(_files.database)
    crs = conn.cursor()

    try:
        crs.executemany(stmt, params)
    except _sql.IntegrityError as e:
        conn.rollback()
        crs.close()
        conn.close()
        raise IntegrityError(e)
    except _sql.OperationalError as e:
        conn.rollback()
        crs.close()
        conn.close()
        if str(e).startswith('no such table: '):
            raise TableDoesNotExist(table_name.lower())
        else:
            raise IntegrityError(e)

    conn.commit()
    crs.close()
    conn.close()

    return


def update(table_name: str, column_definitions: _ColumnDefinitions, row_id: int, row: _Row) -> None:

    _validate_table_name(table_name)
    _validate_columns(table_name, column_definitions)
    _validate_rows(table_name, column_definitions, row)

    columns: list[str] = []
    for i, col_name in enumerate(column_definitions.keys()):
        update_value = row[i]
        if update_value is None:
            columns.append(f'{col_name} = NULL')
        elif column_definitions[col_name] == _ColumnTypes.TEXT:
            columns.append(f'{col_name} = "{row[i]}"')
        else:
            columns.append(f'{col_name} = {row[i]}')
    column_set = ', '.join(columns)
    stmt = f'UPDATE {table_name} SET {column_set} WHERE _ROWID_ = {row_id}'

    with _connect() as crs:
        try:
            crs.execute(stmt)
            if crs.rowcount == 0:
                raise DatabaseException(f'no updates performed on table {table_name}; '
                                        f'is there a record with a row id of {row_id}?')
            elif crs.rowcount > 1:
                raise DatabaseException(f'multiple rows updated in {table_name}; '
                                        f'is row id {row_id} unique for this table?')
        except sqlite3.OperationalError as e:
            raise DatabaseException(f'sql operational error while updating row {row_id} of {table_name}: {e}')

    return


def delete(table_name: str, row_id: int) -> None:

    with _connect() as crs:
        # confirm the table exists
        stmt = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
        crs.execute(stmt)
        rows = crs.fetchall()
        if len(rows) == 0:
            raise TableDoesNotExist(table_name)

        # confirm there is one and only one row in the database with row_id
        stmt = f'SELECT _ROWID_ FROM {table_name} WHERE _ROWID_ = {row_id}'
        crs.execute(stmt)
        rows = crs.fetchall()

        if len(rows) == 0:
            raise InvalidRowId(table_name, row_id)
        if len(rows) > 1:
            raise RowIdNotUnique(table_name, row_id)

        # delete the row
        stmt = f'DELETE FROM {table_name} WHERE _ROWID_ = {row_id}'
        crs.execute(stmt)

    return


def fetch_all(table_name: str) -> list[_Row]:

    _validate_table_name(table_name)

    answer: list[_Row] = []
    stmt = f'SELECT _ROWID_, * FROM {table_name}'

    with _connect() as crs:

        try:
            crs.execute(stmt)
            rows = crs.fetchall()
            answer = [_Row(r) for r in rows]
        except sqlite3.OperationalError as e:
            if str(e).endswith(': syntax error'):
                raise InvalidTableName(table_name)
            if str(e) == f'no such table: {table_name}':
                raise TableDoesNotExist(table_name)

    return answer


def fetch_where(table_name: str, column_definitions: _ColumnDefinitions, where_clause: str) -> list[_Row]:

    _validate_table_name(table_name)
    _validate_columns(table_name, column_definitions)

    answer: list[_Row] = []
    col_names = ', '.join([c for c in column_definitions.keys()])
    stmt = f'SELECT _ROWID_, {col_names} FROM {table_name} WHERE {where_clause}'

    with _connect() as crs:
        try:
            crs.execute(stmt)
            rows = crs.fetchall()
            answer = [_Row(r) for r in rows]
        except sqlite3.OperationalError as e:
            raise DatabaseException(f'store.dbms.fetch_where() sqlite3.OperationalError: {e}')

    return answer


def fetch_distinct(table_name: str, column_name: str) -> list:

    _validate_table_name(table_name)

    with _connect() as crs:
        # confirm the table contains the given column
        crs.execute(f"pragma table_info('{table_name}');")
        rows = crs.fetchall()
        col_names = [str(row[1]) for row in rows]
        if column_name not in col_names:
            raise UndefinedColumnName(column_name)

        # get the distinct values
        stmt = f'SELECT DISTINCT {column_name} FROM {table_name} ORDER BY {column_name}'
        crs.execute(stmt)
        rows = crs.fetchall()

    answer: list = [r[0] for r in rows]

    return answer
