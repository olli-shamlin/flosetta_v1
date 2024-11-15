
from app import app as _app


_database_name = 'rosetta'
_vocab_spreadsheet_name = 'vocabulary'
_kana_spreadsheet_name = 'kana'
_pytest_spreadsheet_name = 'pytest_workbook'
_database_extension = 'sqlite3'
_spreadsheet_extension = 'numbers'


class _FilePath:

    def __init__(self, name: str, ext: str):
        self._name: str = name
        self._extension: str = ext
        self._path = _app.config['DATA_PATH']
        return

    def __str__(self):
        return f'{self.path}/{self.name}.{self.extension}'

    @property
    def path(self) -> str:
        return self._path

    @property
    def name(self) -> str:
        if 'USE_TEST_DB' in _app.config:
            if _app.config['TEST_MODE']:
                return f'test_{self._name}'
        return self._name

    @property
    def extension(self) -> str:
        return self._extension


class _DatabasePath(_FilePath):

    def __init__(self, name: str):
        super().__init__(name, _database_extension)


class _SpreadsheetPath(_FilePath):

    def __init__(self, name: str):
        super().__init__(name, _spreadsheet_extension)


class DataFiles:
    database = str(_DatabasePath(_database_name))
    vocab_spreadsheet = str(_SpreadsheetPath(_vocab_spreadsheet_name))
    kana_spreadsheet = str(_SpreadsheetPath(_kana_spreadsheet_name))
    pytest_spreadsheet = str(_SpreadsheetPath(_pytest_spreadsheet_name))

