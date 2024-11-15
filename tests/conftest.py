
from typing import Optional
import sqlite3 as _sql
from store._data_files import DataFiles as _files


def pytest_collection_modifyitems(session, config, items):
    """The following function fixes the order in which tests are run which is needed in this test suite
       since some tests modify word/character statistics that other tests will reference.
    """
    ordered_tests = [
        # store.dbms tests that must be sequenced
        'test_create_database',
        'test_create_table',
        'test_create_table_unique_column',
        'test_insert',
        'test_insert_with_unique_column',
        'test_insert_many',
        'test_insert_many_with_unique_column',
        'test_update_text_column',
        'test_update_integer_column',
        'test_update_all_columns',
        'test_delete',
        'test_fetch_distinct',

        # store tests that must be sequenced
        'test_store_create_tables',
        'test_populate_tables',

        # execute the tests that validate the initial creation of the test database next
        # *before* testing of *updating* the database happens
        'test_verify_vocab_tables',

        # now test updating the database
        'test_update_database',
    ]

    sequenced_tests = [None] * len(ordered_tests)
    non_sequenced_tests = []

    for fn in items:
        try:
            idx = ordered_tests.index(fn.name)
            sequenced_tests[idx] = fn
        except ValueError:
            # This test (ie, fn) is not in the set of tests that needs to be run in a fixed sequence
            non_sequenced_tests.append(fn)

    # Assure all test that need to be sequenced were found
    if len([fn for fn in sequenced_tests if fn is None]) != 0:
        raise Exception('tests/conftest.py/pytest_collection_modifyitems not all sequenced tests collected')

    items[:] = sequenced_tests + non_sequenced_tests

    return


class CursorContextManager:

    def __init__(self):
        self._connection: Optional[_sql.Connection] = None
        self._cursor: Optional[_sql.Cursor] = None
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
