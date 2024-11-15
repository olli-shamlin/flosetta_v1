
from numbers_parser import Document as _Document


class Row(list):
    pass


class Table:

    def __init__(self, name: str):
        self.name: str = name
        self.columns: list[str] = []
        self.rows: list[Row] = []


class Sheet:

    def __init__(self, name: str):
        self.name: str = name
        self.tables: list[Table] = []


class Workbook:

    def __init__(self):
        self.sheets: list[Sheet] = []


def import_spreadsheet(path: str):

    answer: Workbook = Workbook()
    doc = _Document(path)

    for sheet in doc.sheets:

        next_sheet = Sheet(sheet.name)

        for table in sheet.tables:

            rows = table.rows(values_only=True)
            next_table = Table(table.name)
            next_table.columns = rows[0]
            next_table.rows = [row for row in rows[1:]]
            next_sheet.tables.append(next_table)

        answer.sheets.append(next_sheet)

    return answer
