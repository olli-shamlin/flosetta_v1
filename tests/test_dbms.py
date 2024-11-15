
import store.dbms as dbms
from store._data_files import DataFiles as _files
import os
from os.path import exists
import pytest
import sqlite3 as sql
from conftest import CursorContextManager


def test_create_database():

    # If the test database file exists, delete it; create_database() will fail otherwise
    if os.path.exists(_files.database):
        os.remove(_files.database)

    dbms.create_database()
    assert exists(_files.database)

    # attempt to create the database a second time
    with pytest.raises(FileExistsError) as excinfo:
        dbms.create_database()
    assert str(excinfo.value) == _files.database


def test_create_table():

    cols = dbms.ColumnDefinitions({'col1': dbms.ColumnTypes.TEXT,
                                   'col2': dbms.ColumnTypes.TEXT,
                                   'col3': dbms.ColumnTypes.INTEGER})
    dbms.create_table('my_table', cols)

    with CursorContextManager() as crs:
        # Confirm the database now has one and only one table named "my_table"
        crs.execute('SELECT name FROM sqlite_schema WHERE type = "table" AND name NOT LIKE "sqlite_%"')
        rows = crs.fetchall()

        assert len(rows) == 1
        assert len(rows[0]) == 1
        assert rows[0][0] == 'my_table'

        # Confirm my_table's columns are as expected
        crs.execute("pragma table_info('my_table');")
        rows = crs.fetchall()

        assert len(rows) == 3
        assert (rows[0][1], rows[0][2]) == ('col1', 'TEXT')
        assert (rows[1][1], rows[1][2]) == ('col2', 'TEXT')
        assert (rows[2][1], rows[2][2]) == ('col3', 'INTEGER')

    return


def test_create_table_unique_column():

    cols = {
        'col1': dbms.ColumnTypes.TEXT,
        'col2': dbms.ColumnTypes.TEXT,
        'col3': dbms.ColumnTypes.INTEGER
    }
    cols_def = dbms.ColumnDefinitions(cols, unique_column='col1')

    dbms.create_table('my_table2', cols_def)

    # Confirm the database now has two tables
    with CursorContextManager() as crs:
        crs.execute('SELECT name FROM sqlite_schema WHERE type = "table" AND name NOT LIKE "sqlite_%"')
        rows = crs.fetchall()

        assert len(rows) == 2
        assert len(rows[0]) == 1
        assert rows[0][0] == 'my_table'
        assert len(rows[1]) == 1
        assert rows[1][0] == 'my_table2'

        # Confirm my_table's columns are as expected
        crs.execute("SELECT sql FROM sqlite_schema WHERE name = 'my_table2'")
        rows = crs.fetchall()

        assert len(rows) == 1 and len(rows[0]) == 1
        assert rows[0][0] == 'CREATE TABLE my_table2 (col1 TEXT NOT NULL UNIQUE, col2 TEXT, col3 INTEGER)'

    return


def test_create_table_exists():

    # Attempting to create a table that already exists should raise a meaningful exception
    with pytest.raises(sql.OperationalError) as excinfo:
        cols = dbms.ColumnDefinitions({'col1': dbms.ColumnTypes.TEXT,
                                       'col2': dbms.ColumnTypes.TEXT,
                                       'col3': dbms.ColumnTypes.INTEGER})
        dbms.create_table('my_table', cols)
    assert str(excinfo.value) == 'table my_table already exists'

    return


def test_bad_column_definitions():

    with pytest.raises(dbms.InvalidColumnType) as excinfo:
        dbms.ColumnDefinitions({'col1': 3})  # a bad column type
    assert str(excinfo.value) == 'invalid column type: "3" for column col1'

    with pytest.raises(dbms.InvalidColumnType) as excinfo:
        dbms.ColumnDefinitions({'col1': 'str'})  # a bad column type
    assert str(excinfo.value) == 'invalid column type: "str" for column col1'

    with pytest.raises(dbms.InvalidColumnType) as excinfo:
        dbms.ColumnDefinitions({'col1': int})  # a bad column type
    assert str(excinfo.value) == "invalid column type: \"<class 'int'>\" for column col1"

    return


def test_insert():

    cols = dbms.ColumnDefinitions({'col1': dbms.ColumnTypes.TEXT,
                                   'col2': dbms.ColumnTypes.TEXT,
                                   'col3': dbms.ColumnTypes.INTEGER})
    rows = [
        dbms.Row(['row-1 col-1', 'row-1 col-2', 1]),
        dbms.Row(['row-2 col-1', 'row-2 col-2', 2]),
        dbms.Row(['row-3 col-1', 'row-3 col-2', 3]),
    ]

    expected_rowid = 1
    for row in rows:
        rowid = dbms.insert('my_table', cols, row)
        assert rowid == expected_rowid
        expected_rowid += 1

    # Assure the table now has the rows just inserted
    with CursorContextManager() as crs:
        crs.execute('SELECT _ROWID_, * from my_table')
        rows = crs.fetchall()

        assert len(rows) == 3
        row = rows[0]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (1, 'row-1 col-1', 'row-1 col-2', 1)
        row = rows[1]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (2, 'row-2 col-1', 'row-2 col-2', 2)
        row = rows[2]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (3, 'row-3 col-1', 'row-3 col-2', 3)

    return


def test_insert_with_bad_table():

    cols = dbms.ColumnDefinitions({'col1': dbms.ColumnTypes.TEXT,
                                   'col2': dbms.ColumnTypes.TEXT,
                                   'col3': dbms.ColumnTypes.INTEGER})

    with pytest.raises(dbms.TableDoesNotExist) as excinfo:
        dbms.insert('bad_name', cols, dbms.Row(['row-1 col-1', 'row-1 col-2', 1]))
    assert str(excinfo.value) == 'no such table: bad_name'

    return


def test_insert_with_bad_column_names():

    cols = dbms.ColumnDefinitions({'bad-syntax': dbms.ColumnTypes.TEXT,
                                   'col2': dbms.ColumnTypes.TEXT,
                                   'col3': dbms.ColumnTypes.INTEGER})

    with pytest.raises(dbms.UndefinedColumnName) as excinfo:
        dbms.insert('my_table', cols, dbms.Row(['row-1 col-1', 'row-1 col-2', 1]))
    assert str(excinfo.value) == 'undefined column name: bad-syntax'

    cols = dbms.ColumnDefinitions({'bad_name': dbms.ColumnTypes.TEXT,
                                   'col2': dbms.ColumnTypes.TEXT,
                                   'col3': dbms.ColumnTypes.INTEGER})

    with pytest.raises(dbms.UndefinedColumnName) as excinfo:
        dbms.insert('my_table', cols, dbms.Row(['row-1 col-1', 'row-1 col-2', 1]))
    assert str(excinfo.value) == 'undefined column name: bad_name'

    return


def test_insert_with_unique_column():

    cols = dbms.ColumnDefinitions({'col1': dbms.ColumnTypes.TEXT,
                                   'col2': dbms.ColumnTypes.TEXT,
                                   'col3': dbms.ColumnTypes.INTEGER})

    # Attempt to insert the exact same row of data twice; the second time should fail
    dbms.insert('my_table2', cols, dbms.Row(['row-1 col-1', 'row-1 col-2', 1]))
    with pytest.raises(dbms.IntegrityError) as excinfo:
        dbms.insert('my_table2', cols, dbms.Row(['row-1 col-1', 'row-1 col-2', 1]))
    assert str(excinfo.value) == 'UNIQUE constraint failed: my_table2.col1'

    # Assure the table now has the row just successfully inserted
    with CursorContextManager() as crs:
        crs.execute('SELECT _ROWID_, * from my_table2')
        rows = crs.fetchall()

        assert len(rows) == 1
        row = rows[0]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (1, 'row-1 col-1', 'row-1 col-2', 1)

    return


def test_insert_many():

    cols = dbms.ColumnDefinitions({'col1': dbms.ColumnTypes.TEXT,
                                   'col2': dbms.ColumnTypes.TEXT,
                                   'col3': dbms.ColumnTypes.INTEGER})
    rows = [
        dbms.Row(['row-4 col-1', 'row-4 col-2', 4]),
        dbms.Row(['row-5 col-1', 'row-5 col-2', 5]),
        dbms.Row(['row-6 col-1', 'row-6 col-2', 6]),
    ]

    dbms.insert_many('my_table', cols, rows)

    # Assure the table now has the rows just inserted
    with CursorContextManager() as crs:
        crs.execute('SELECT _ROWID_, * from my_table')
        rows = crs.fetchall()

        assert len(rows) == 6
        row = rows[3]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (4, 'row-4 col-1', 'row-4 col-2', 4)
        row = rows[4]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (5, 'row-5 col-1', 'row-5 col-2', 5)
        row = rows[5]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (6, 'row-6 col-1', 'row-6 col-2', 6)

    return


def test_insert_many_with_unique_column():

    cols = dbms.ColumnDefinitions({'col1': dbms.ColumnTypes.TEXT,
                                   'col2': dbms.ColumnTypes.TEXT,
                                   'col3': dbms.ColumnTypes.INTEGER})
    rows = [
        dbms.Row(['row-2 col-1', 'row-2 col-2', 2]),
        dbms.Row(['row-3 col-1', 'row-3 col-2', 3]),
        dbms.Row(['row-4 col-1', 'row-4 col-2', 4]),
    ]

    dbms.insert_many('my_table2', cols, rows)

    # Assure the table now has the rows just inserted
    with CursorContextManager() as crs:
        crs.execute('SELECT _ROWID_, * from my_table2')
        rows = crs.fetchall()

        assert len(rows) == 4
        row = rows[1]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (2, 'row-2 col-1', 'row-2 col-2', 2)
        row = rows[2]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (3, 'row-3 col-1', 'row-3 col-2', 3)
        row = rows[3]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (4, 'row-4 col-1', 'row-4 col-2', 4)

    return


def test_insert_many_with_unique_column_and_dup_value():

    cols = dbms.ColumnDefinitions({'col1': dbms.ColumnTypes.TEXT,
                                   'col2': dbms.ColumnTypes.TEXT,
                                   'col3': dbms.ColumnTypes.INTEGER})
    # Note the 3rd row has the same col1 value as the 1st row.  This should result in
    # a Sqlite3 IntegrityError exception *AND* none of the rows should get added to the table
    rows = [
        dbms.Row(['row-5 col-1', 'row-5 col-2', 5]),
        dbms.Row(['row-6 col-1', 'row-6 col-2', 6]),
        dbms.Row(['row-5 col-1', 'row-7 col-2', 7]),
    ]

    with pytest.raises(dbms.IntegrityError) as excinfo:
        dbms.insert_many('my_table2', cols, rows)
    assert str(excinfo.value) == 'UNIQUE constraint failed: my_table2.col1'

    # Assure the table now has the rows just inserted
    with CursorContextManager() as crs:
        crs.execute('SELECT _ROWID_, * from my_table2')
        rows = crs.fetchall()

        assert len(rows) == 4
        row = rows[0]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (1, 'row-1 col-1', 'row-1 col-2', 1)
        row = rows[1]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (2, 'row-2 col-1', 'row-2 col-2', 2)
        row = rows[2]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (3, 'row-3 col-1', 'row-3 col-2', 3)
        row = rows[3]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (4, 'row-4 col-1', 'row-4 col-2', 4)

    return


def test_insert_many_with_bad_table_name():

    cols = dbms.ColumnDefinitions({'col1': dbms.ColumnTypes.TEXT,
                                   'col2': dbms.ColumnTypes.TEXT,
                                   'col3': dbms.ColumnTypes.INTEGER})
    rows = [
        dbms.Row(['row-5 col-1', 'row-5 col-2', 5]),
        dbms.Row(['row-6 col-1', 'row-6 col-2', 6]),
        dbms.Row(['row-7 col-1', 'row-7 col-2', 7]),
    ]

    with pytest.raises(dbms.TableDoesNotExist) as excinfo:
        dbms.insert_many('bad_name', cols, rows)
    assert str(excinfo.value) == 'no such table: bad_name'

    # Assure the table now has the rows just inserted
    with CursorContextManager() as crs:
        crs.execute('SELECT _ROWID_, * from my_table2')
        rows = crs.fetchall()

        assert len(rows) == 4
        row = rows[0]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (1, 'row-1 col-1', 'row-1 col-2', 1)
        row = rows[1]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (2, 'row-2 col-1', 'row-2 col-2', 2)
        row = rows[2]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (3, 'row-3 col-1', 'row-3 col-2', 3)
        row = rows[3]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (4, 'row-4 col-1', 'row-4 col-2', 4)

    return


def test_insert_many_with_bad_column_name():

    cols = dbms.ColumnDefinitions({'col1': dbms.ColumnTypes.TEXT,
                                   'BAD_NAME': dbms.ColumnTypes.TEXT,
                                   'col3': dbms.ColumnTypes.INTEGER})
    rows = [
        dbms.Row(['row-5 col-1', 'row-5 col-2', 5]),
        dbms.Row(['row-6 col-1', 'row-6 col-2', 6]),
        dbms.Row(['row-7 col-1', 'row-7 col-2', 7]),
    ]

    with pytest.raises(dbms.UndefinedColumnName) as excinfo:
        dbms.insert_many('my_table2', cols, rows)
    assert str(excinfo.value) == 'undefined column name: bad_name'

    return


def test_update_text_column():

    cols = dbms.ColumnDefinitions({'col1': dbms.ColumnTypes.TEXT})
    row = dbms.Row(['row-3 col-1 UPDATED'])

    dbms.update('my_table', column_definitions=cols, row_id=3, row=row)

    # Assure the update was correctly applied
    with CursorContextManager() as crs:
        crs.execute('SELECT _ROWID_, * from my_table')
        rows = crs.fetchall()

        assert len(rows) == 6
        row = rows[0]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (1, 'row-1 col-1', 'row-1 col-2', 1)
        row = rows[1]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (2, 'row-2 col-1', 'row-2 col-2', 2)
        row = rows[2]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (3, 'row-3 col-1 UPDATED', 'row-3 col-2', 3)
        row = rows[3]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (4, 'row-4 col-1', 'row-4 col-2', 4)
        row = rows[4]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (5, 'row-5 col-1', 'row-5 col-2', 5)
        row = rows[5]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (6, 'row-6 col-1', 'row-6 col-2', 6)

    return


def test_update_integer_column():

    cols = dbms.ColumnDefinitions({'col3': dbms.ColumnTypes.INTEGER})
    row = dbms.Row([100])

    dbms.update('my_table', column_definitions=cols, row_id=3, row=row)

    # Assure the update was correctly applied
    with CursorContextManager() as crs:
        crs.execute('SELECT _ROWID_, * from my_table')
        rows = crs.fetchall()

        assert len(rows) == 6
        row = rows[0]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (1, 'row-1 col-1', 'row-1 col-2', 1)
        row = rows[1]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (2, 'row-2 col-1', 'row-2 col-2', 2)
        row = rows[2]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (3, 'row-3 col-1 UPDATED', 'row-3 col-2', 100)
        row = rows[3]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (4, 'row-4 col-1', 'row-4 col-2', 4)
        row = rows[4]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (5, 'row-5 col-1', 'row-5 col-2', 5)
        row = rows[5]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (6, 'row-6 col-1', 'row-6 col-2', 6)

    return


def test_update_all_columns():

    cols = dbms.ColumnDefinitions({
        'col1': dbms.ColumnTypes.TEXT,
        'col2': dbms.ColumnTypes.TEXT,
        'col3': dbms.ColumnTypes.INTEGER,
    })
    row = dbms.Row(['row-4 col-1 UPDATED', 'row-4 col-2 UPDATED', 1999])

    dbms.update('my_table', column_definitions=cols, row_id=4, row=row)

    # Assure the update was correctly applied
    with CursorContextManager() as crs:
        crs.execute('SELECT _ROWID_, * from my_table')
        rows = crs.fetchall()

        assert len(rows) == 6
        row = rows[0]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (1, 'row-1 col-1', 'row-1 col-2', 1)
        row = rows[1]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (2, 'row-2 col-1', 'row-2 col-2', 2)
        row = rows[2]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (3, 'row-3 col-1 UPDATED', 'row-3 col-2', 100)
        row = rows[3]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (4, 'row-4 col-1 UPDATED', 'row-4 col-2 UPDATED', 1999)
        row = rows[4]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (5, 'row-5 col-1', 'row-5 col-2', 5)
        row = rows[5]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (6, 'row-6 col-1', 'row-6 col-2', 6)

    return


def test_update_bad_table_name():

    cols = dbms.ColumnDefinitions({
        'col1': dbms.ColumnTypes.TEXT,
        'col2': dbms.ColumnTypes.TEXT,
        'col3': dbms.ColumnTypes.INTEGER,
    })
    row = dbms.Row(['will not get updated', 'table name is bad syntax', -25])

    with pytest.raises(dbms.TableDoesNotExist) as excinfo:
        dbms.update('bad$name', column_definitions=cols, row_id=6, row=row)
    assert str(excinfo.value) == 'no such table: bad$name'

    # Assure the update was correctly applied
    with CursorContextManager() as crs:
        crs.execute('SELECT _ROWID_, * from my_table')
        rows = crs.fetchall()

        assert len(rows) == 5
        row = rows[0]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (1, 'row-1 col-1', 'row-1 col-2', 1)
        row = rows[1]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (2, 'row-2 col-1', 'row-2 col-2', 2)
        row = rows[2]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (3, 'row-3 col-1 UPDATED', 'row-3 col-2', 100)
        row = rows[3]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (4, 'row-4 col-1 UPDATED', 'row-4 col-2 UPDATED', 1999)
        row = rows[4]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (5, 'row-5 col-1', 'row-5 col-2', 5)

    return


def test_update_unknown_table_name():

    cols = dbms.ColumnDefinitions({
        'col1': dbms.ColumnTypes.TEXT,
        'col2': dbms.ColumnTypes.TEXT,
        'col3': dbms.ColumnTypes.INTEGER,
    })
    row = dbms.Row(['will not get updated', 'table name is undefined', -25])

    with pytest.raises(dbms.TableDoesNotExist) as excinfo:
        dbms.update('unknown_table', column_definitions=cols, row_id=6, row=row)
    assert str(excinfo.value) == 'no such table: unknown_table'

    # Assure the update was correctly applied
    with CursorContextManager() as crs:
        crs.execute('SELECT _ROWID_, * from my_table')
        rows = crs.fetchall()

        assert len(rows) == 5
        row = rows[0]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (1, 'row-1 col-1', 'row-1 col-2', 1)
        row = rows[1]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (2, 'row-2 col-1', 'row-2 col-2', 2)
        row = rows[2]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (3, 'row-3 col-1 UPDATED', 'row-3 col-2', 100)
        row = rows[3]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (4, 'row-4 col-1 UPDATED', 'row-4 col-2 UPDATED', 1999)
        row = rows[4]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (5, 'row-5 col-1', 'row-5 col-2', 5)

    return


def test_update_bad_id():

    cols = dbms.ColumnDefinitions({
        'col1': dbms.ColumnTypes.TEXT,
        'col2': dbms.ColumnTypes.TEXT,
        'col3': dbms.ColumnTypes.INTEGER,
    })
    row = dbms.Row(['will not get updated', 'row id is bad', -25])

    with pytest.raises(dbms.DatabaseException) as excinfo:
        dbms.update('my_table', column_definitions=cols, row_id=50, row=row)
    assert str(excinfo.value) == 'no updates performed on table my_table; is there a record with a row id of 50?'

    # Assure the update was correctly applied
    with CursorContextManager() as crs:
        crs.execute('SELECT _ROWID_, * from my_table')
        rows = crs.fetchall()

        assert len(rows) == 5
        row = rows[0]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (1, 'row-1 col-1', 'row-1 col-2', 1)
        row = rows[1]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (2, 'row-2 col-1', 'row-2 col-2', 2)
        row = rows[2]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (3, 'row-3 col-1 UPDATED', 'row-3 col-2', 100)
        row = rows[3]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (4, 'row-4 col-1 UPDATED', 'row-4 col-2 UPDATED', 1999)
        row = rows[4]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (5, 'row-5 col-1', 'row-5 col-2', 5)

    return


def test_update_bad_column_name():

    cols = dbms.ColumnDefinitions({
        'col1': dbms.ColumnTypes.TEXT,
        'bad_column': dbms.ColumnTypes.TEXT,
        'col3': dbms.ColumnTypes.INTEGER,
    })
    row = dbms.Row(['will not get updated', '"bad_column" does not exist', -25])

    with pytest.raises(dbms.DatabaseException) as excinfo:
        dbms.update('my_table', column_definitions=cols, row_id=1, row=row)
    assert str(excinfo.value) == 'undefined column name: bad_column'

    # Assure the update was correctly applied
    with CursorContextManager() as crs:
        crs.execute('SELECT _ROWID_, * from my_table')
        rows = crs.fetchall()

        assert len(rows) == 5
        row = rows[0]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (1, 'row-1 col-1', 'row-1 col-2', 1)
        row = rows[1]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (2, 'row-2 col-1', 'row-2 col-2', 2)
        row = rows[2]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (3, 'row-3 col-1 UPDATED', 'row-3 col-2', 100)
        row = rows[3]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (4, 'row-4 col-1 UPDATED', 'row-4 col-2 UPDATED', 1999)
        row = rows[4]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (5, 'row-5 col-1', 'row-5 col-2', 5)

    return


def test_update_bad_data_type():

    cols = dbms.ColumnDefinitions({
        'col1': dbms.ColumnTypes.TEXT,
        'col2': dbms.ColumnTypes.INTEGER,
        'col3': dbms.ColumnTypes.INTEGER,
    })
    row = dbms.Row(['will not get updated', 'data type for col2 in ColDef is wrong', -25])

    with pytest.raises(dbms.InvalidColumnType) as excinfo:
        dbms.update('my_table', column_definitions=cols, row_id=1, row=row)
    assert str(excinfo.value) == 'invalid column type: "ColumnTypes.INTEGER" for column col2'

    # Assure the update was correctly applied
    with CursorContextManager() as crs:
        crs.execute('SELECT _ROWID_, * from my_table')
        rows = crs.fetchall()

        assert len(rows) == 5
        row = rows[0]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (1, 'row-1 col-1', 'row-1 col-2', 1)
        row = rows[1]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (2, 'row-2 col-1', 'row-2 col-2', 2)
        row = rows[2]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (3, 'row-3 col-1 UPDATED', 'row-3 col-2', 100)
        row = rows[3]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (4, 'row-4 col-1 UPDATED', 'row-4 col-2 UPDATED', 1999)
        row = rows[4]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (5, 'row-5 col-1', 'row-5 col-2', 5)

    return


def test_delete():

    dbms.delete('my_table', row_id=6)

    # Assure the correct row was deleted
    with CursorContextManager() as crs:
        crs.execute('SELECT _ROWID_, * from my_table')
        rows = crs.fetchall()

        assert len(rows) == 5
        row = rows[0]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (1, 'row-1 col-1', 'row-1 col-2', 1)
        row = rows[1]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (2, 'row-2 col-1', 'row-2 col-2', 2)
        row = rows[2]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (3, 'row-3 col-1 UPDATED', 'row-3 col-2', 100)
        row = rows[3]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (4, 'row-4 col-1 UPDATED', 'row-4 col-2 UPDATED', 1999)
        row = rows[4]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (5, 'row-5 col-1', 'row-5 col-2', 5)

    return


def test_delete_bad_row_id():

    with pytest.raises(dbms.InvalidRowId) as excinfo:
        dbms.delete('my_table', row_id=59)
    assert str(excinfo.value) == 'no rows with an id of 59 exists in table my_table'

    # Assure the correct row was deleted
    with CursorContextManager() as crs:
        crs.execute('SELECT _ROWID_, * from my_table')
        rows = crs.fetchall()

        assert len(rows) == 5
        row = rows[0]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (1, 'row-1 col-1', 'row-1 col-2', 1)
        row = rows[1]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (2, 'row-2 col-1', 'row-2 col-2', 2)
        row = rows[2]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (3, 'row-3 col-1 UPDATED', 'row-3 col-2', 100)
        row = rows[3]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (4, 'row-4 col-1 UPDATED', 'row-4 col-2 UPDATED', 1999)
        row = rows[4]
        assert len(row) == 4 and (row[0], row[1], row[2], row[3]) == (5, 'row-5 col-1', 'row-5 col-2', 5)

    return


def test_fetch_all():

    rows = dbms.fetch_all('my_table')

    assert len(rows) == 5
    assert rows[0] == [1, 'row-1 col-1', 'row-1 col-2', 1]
    assert rows[1] == [2, 'row-2 col-1', 'row-2 col-2', 2]
    assert rows[2] == [3, 'row-3 col-1 UPDATED', 'row-3 col-2', 100]
    assert rows[3] == [4, 'row-4 col-1 UPDATED', 'row-4 col-2 UPDATED', 1999]
    assert rows[4] == [5, 'row-5 col-1', 'row-5 col-2', 5]

    return


def test_fetch_all_bad_table_name():

    with pytest.raises(dbms.TableDoesNotExist) as excinfo:
        dbms.fetch_all('my table')
    assert str(excinfo.value) == 'no such table: my table'

    with pytest.raises(dbms.TableDoesNotExist) as excinfo:
        dbms.fetch_all('bad_table')
    assert str(excinfo.value) == 'no such table: bad_table'

    return


def test_fetch_distinct():

    # Set up a table to test with
    table_name = 'distinct_values'
    cols = dbms.ColumnDefinitions({'col1': dbms.ColumnTypes.TEXT,
                                   'col2': dbms.ColumnTypes.TEXT})
    dbms.create_table(table_name, cols)

    rows: list[dbms.Row] = []
    for i in range(1, 100):
        rows.append(dbms.Row([f'row {i}', f'value {(i % 5) + 1}']))

    dbms.insert_many(table_name, cols, rows)

    distinct_values = dbms.fetch_distinct(table_name, column_name='col2')

    assert len(distinct_values) == 5
    assert distinct_values[0] == 'value 1'
    assert distinct_values[1] == 'value 2'
    assert distinct_values[2] == 'value 3'
    assert distinct_values[3] == 'value 4'
    assert distinct_values[4] == 'value 5'

    return


def test_fetch_distinct_bad_table_name():

    with pytest.raises(dbms.TableDoesNotExist) as excinfo:
        dbms.fetch_distinct('bad name syntax', column_name='col2')
    assert str(excinfo.value) == 'no such table: bad name syntax'

    with pytest.raises(dbms.TableDoesNotExist) as excinfo:
        dbms.fetch_distinct('undefined_table', column_name='col2')
    assert str(excinfo.value) == 'no such table: undefined_table'

    return


def test_fetch_distinct_bad_column_name():

    with pytest.raises(dbms.UndefinedColumnName) as excinfo:
        dbms.fetch_distinct('distinct_values', column_name='$#! bad syntax')
    assert str(excinfo.value) == 'undefined column name: $#! bad syntax'

    with pytest.raises(dbms.UndefinedColumnName) as excinfo:
        dbms.fetch_distinct('distinct_values', column_name='undefined_column')
    assert str(excinfo.value) == 'undefined column name: undefined_column'

    return


def test_null_values():

    # Set up a table to test with
    table_name = 'null_values'
    cols = dbms.ColumnDefinitions({'col1': dbms.ColumnTypes.TEXT,
                                   'col2': dbms.ColumnTypes.INTEGER})
    dbms.create_table(table_name, cols)

    rows: list[dbms.Row] = []
    for i in range(1, 11):
        if i % 2:
            rows.append(dbms.Row([f'row {i}', None]))
        else:
            rows.append(dbms.Row([None, i]))

    dbms.insert_many(table_name, cols, rows)

    rows = dbms.fetch_all(table_name)
    assert len(rows) == 10
    row = rows[0]
    assert row == [1, 'row 1', None]
    row = rows[1]
    assert row == [2, None, 2]
    row = rows[2]
    assert row == [3, 'row 3', None]
    row = rows[3]
    assert row == [4, None, 4]
    row = rows[4]
    assert row == [5, 'row 5', None]
    row = rows[5]
    assert row == [6, None, 6]
    row = rows[6]
    assert row == [7, 'row 7', None]
    row = rows[7]
    assert row == [8, None, 8]
    row = rows[8]
    assert row == [9, 'row 9', None]
    row = rows[9]
    assert row == [10, None, 10]

    return
