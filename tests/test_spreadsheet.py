
from store.spreadsheet import import_spreadsheet
from store._data_files import DataFiles as _files


def test_import_vocab():

    workbook = import_spreadsheet(_files.pytest_spreadsheet)

    # Assure there are the number of expected sheets and tables per sheet
    assert len(workbook.sheets) == 3
    assert len(workbook.sheets[0].tables) == 2
    assert len(workbook.sheets[1].tables) == 3
    assert len(workbook.sheets[2].tables) == 4

    # Assure the tables on the first sheet have the expected number of rows and columns
    assert len(workbook.sheets[0].tables[0].columns) == 3
    assert len(workbook.sheets[0].tables[0].rows) == 3
    assert len(workbook.sheets[0].tables[1].columns) == 3
    assert len(workbook.sheets[0].tables[1].rows) == 3

    # Assure the tables on the second sheet have the expected number of rows and columns
    assert len(workbook.sheets[1].tables[0].columns) == 4
    assert len(workbook.sheets[1].tables[0].rows) == 4
    assert len(workbook.sheets[1].tables[1].columns) == 4
    assert len(workbook.sheets[1].tables[1].rows) == 4
    assert len(workbook.sheets[1].tables[2].columns) == 4
    assert len(workbook.sheets[1].tables[2].rows) == 4

    # Assure the tables on the third sheet have the expected number of rows and columns
    assert len(workbook.sheets[2].tables[0].columns) == 5
    assert len(workbook.sheets[2].tables[0].rows) == 5
    assert len(workbook.sheets[2].tables[1].columns) == 5
    assert len(workbook.sheets[2].tables[1].rows) == 5
    assert len(workbook.sheets[2].tables[2].columns) == 5
    assert len(workbook.sheets[2].tables[2].rows) == 5
    assert len(workbook.sheets[2].tables[3].columns) == 5
    assert len(workbook.sheets[2].tables[3].rows) == 5

    # Assure the cells in each table have the expected values
    sidx = 0
    for sheet in workbook.sheets:
        sidx += 1
        for table in sheet.tables:
            # Note: the order in which tables are returned per sheet is not stable
            # So we can't depend on the enumerate function to be a value that matches the next table
            tidx = int(table.name.split('-')[-1])
            cidx = 0
            for column in table.columns:
                cidx += 1
                assert column == f'S{sidx}-T{tidx}-C{cidx}'
            ridx = 0
            for row in table.rows:
                ridx += 1
                cidx = 0
                for cell in row:
                    cidx += 1
                    assert cell == f'S{sidx}-T{tidx}-C{cidx}-R{ridx}'

    return
