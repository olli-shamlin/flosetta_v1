
import os
import sqlite3
from sqlite3 import Connection, Cursor
from app import app
from app.utils import FilePaths as files, debug_msg, tracer
from app.utils.exceptions import DatabaseExists
from app.model.spreadsheet import import_kana, import_vocab


class _Schema:

    def __init__(self, create_stmt: str, cols: list[str]):
        self.create_statement: str = create_stmt
        self.columns: list[str] = cols

    @property
    def sql_column_list(self) -> str:
        return ', '.join(self.columns)

    @property
    def sql_values_list(self) -> str:
        return ', '.join(['?'] * len(self.columns))


_SQL_NULL = None
_STATS_SQL = 'quizzed INTEGER, correct INTEGER, consecutive_correct INTEGER, consecutive_wrong INTEGER'
_STATS_COLS = ['quizzed', 'correct', 'consecutive_correct', 'consecutive_wrong']
_DEFAULT_STATS = [0, 0, 0, 0]


class _Schemas:
    vocab = _Schema(
        f'CREATE TABLE vocab '
        f'(english_w TEXT, romaji_w TEXT, kana_w TEXT, kanji_w TEXT, pos TEXT, note TEXT, tag TEXT, '
        f'{_STATS_SQL})',
        ['english_w', 'romaji_w', 'kana_w', 'kanji_w', 'pos', 'note', 'tag'] + _STATS_COLS
    )
    kana = _Schema(
        f'CREATE TABLE kana (romaji TEXT, hiragana TEXT, hiragana_mnemonic TEXT, katakana TEXT, katakana_mnemonic, '
        f'category TEXT, {_STATS_SQL})',
        ['romaji', 'hiragana', 'hiragana_mnemonic', 'katakana', 'katakana_mnemonic', 'category'] + _STATS_COLS
    )


@tracer
def _connect() -> Connection:

    db_path = files.test_database.full_path if app.config['USE_TEST_DB'] else files.prod_database.full_path
    dbcon = sqlite3.connect(db_path)
    dbcon.execute('PRAGMA foreign_keys=ON;')

    return dbcon


@tracer
def _insert_kana_rows(csr: Cursor):

    debug_msg('inserting kana rows into database')

    kana_rows = import_kana()
    rows = [[v for v in r.values()] + _DEFAULT_STATS for r in kana_rows]

    stmt = f"INSERT INTO kana ({_Schemas.kana.sql_column_list}) VALUES ({_Schemas.kana.sql_values_list})"
    csr.executemany(stmt, rows)

    debug_msg('done inserting kana rows into database')
    return


@tracer
def _insert_test_vocab_rows(csr: Cursor):

    debug_msg('inserting TEST vocab rows into database')
    stat_vals = [0, 0, 0, 0]

    rows = list()
    for i in range(1, 101):
        note = f'W{i} note' if i % 2 else _SQL_NULL
        num_tags = i % 4
        tags = '; '.join([f'W{i}T{j}' for j in range(1, num_tags+1)]) if num_tags else _SQL_NULL
        next_row = [f'W{i} english', f'W{i} romaji', f'W{i} kana', f'W{i} kanji', f'W{i} pos', note, tags]
        next_row.extend(stat_vals)
        rows.append(next_row)

    stmt = f"INSERT INTO vocab ({_Schemas.vocab.sql_column_list}) VALUES ({_Schemas.vocab.sql_values_list})"
    csr.executemany(stmt, rows)

    debug_msg('done inserting TEST vocab rows into database')
    return


def _insert_prod_vocab_rows(csr: Cursor):

    debug_msg('inserting vocab rows into database')
    vocab_rows = import_vocab()
    stat_vals = [0, 0, 0, 0]

    rows = list()
    for r in vocab_rows:
        next_row = [r['english'], r['romaji'], r['kana'], r['kanji'], r['pos'], r['note'], r['tags']]
        next_row.extend(stat_vals)
        rows.append(next_row)

    stmt = f"INSERT INTO vocab ({_Schemas.vocab.sql_column_list}) VALUES ({_Schemas.vocab.sql_values_list})"
    csr.executemany(stmt, rows)

    debug_msg('done inserting vocab rows into database')
    return


@tracer
def _insert_test_rows(csr: Cursor):

    _insert_test_vocab_rows(csr)
    _insert_kana_rows(csr)

    return


@tracer
def create():

    dbms_path = files.test_database.full_path if app.config['USE_TEST_DB'] else files.prod_database.full_path

    debug_msg('creating database')
    debug_msg(f'app.config["USE_TEST_DB"] = {app.config["USE_TEST_DB"]}')
    debug_msg(f'database path: {dbms_path}')

    if os.path.exists(dbms_path):
        raise DatabaseExists(dbms_path)

    dbcon = _connect()

    cursor = dbcon.cursor()
    cursor.execute(_Schemas.vocab.create_statement)
    cursor.execute(_Schemas.kana.create_statement)

    if app.config['USE_TEST_DB']:
        _insert_test_rows(cursor)
    else:
        _insert_prod_vocab_rows(cursor)
        _insert_kana_rows(cursor)

    cursor.close()
    dbcon.commit()
    dbcon.close()

    debug_msg(f'done creating database: {dbms_path}')
    return


@tracer
def _fetch_all(select_stmt: str) -> list[tuple]:

    dbcon = _connect()
    cursor = dbcon.cursor()

    cursor.execute(select_stmt)
    rows = cursor.fetchall()

    cursor.close()
    dbcon.close()

    return rows


@tracer
def fetch_kana() -> list[tuple]:
    return _fetch_all('SELECT _ROWID_, * FROM kana')


@tracer
def fetch_vocab() -> list[tuple]:
    return _fetch_all('SELECT _ROWID_, * FROM vocab')


@tracer
def fetch_parts_of_speech() -> list[tuple]:
    return _fetch_all('SELECT DISTINCT pos FROM vocab ORDER BY pos')


@tracer
def fetch_kana_categories() -> list[tuple]:
    return _fetch_all('SELECT DISTINCT category FROM kana ORDER BY category')


@tracer
def fetch_word_tags() -> list[tuple]:
    return _fetch_all('SELECT DISTINCT tag FROM vocab WHERE tag IS NOT NULL')


@tracer
def update_row(table: str, rec_id: int, col_value_map: dict[str, int]) -> None:

    # TODO: modify update row to support other column values types besides INTEGER
    # This routine currently only handles updating integer column values; if I figure out
    # how to implement a script that can be run in this project to create/update the DBMS,
    # I'm likely going to want this function to be more flexible (ie, handle str/TEXT and
    # None/NULL column values too!
    columns: list[str] = []
    for col_name, col_value in col_value_map.items():
        columns.append(f'{col_name} = {col_value}')
    column_set = ', '.join(columns)

    stmt = f'UPDATE {table} SET {column_set} WHERE _ROWID_ = {rec_id}'

    dbcon = _connect()
    csr = dbcon.cursor()

    csr.execute(stmt)
    assert csr.rowcount == 1

    csr.close()
    dbcon.commit()
    dbcon.close()

    return
