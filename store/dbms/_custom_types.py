
# TODO change this module's name from "_custom_types.py" to "_types.py"

from collections import UserDict as _UserDict
from collections import UserList as _UserList
from enum import Enum as _Enum
from ._exceptions import UndefinedColumnName, InvalidColumnNameType, InvalidColumnType
from typing import Optional as _Optional


class ColumnTypes(_Enum):
    INTEGER = 'INTEGER'
    TEXT = 'TEXT'


class ColumnDefinitions(_UserDict):

    def __init__(self, dict_inst=None, unique_column: str = None):
        super().__init__(dict_inst)

        if unique_column:
            unique_column = unique_column.lower()
            if unique_column not in self.data.keys():
                raise UndefinedColumnName(unique_column)

        self._unique_column: str = unique_column
        return

    def __setitem__(self, key, value):
        if not isinstance(key, str):
            raise InvalidColumnNameType(key)
        if not isinstance(value, ColumnTypes):
            raise InvalidColumnType(key, value)
        self.data[key.lower()] = value

    def __getitem__(self, key):
        return self.data[key.lower()]

    @property
    def unique_column(self) -> _Optional[str]:
        return self._unique_column


class Row(_UserList):

    def __setitem__(self, index, value):

        if not (isinstance(value, str) or isinstance(value, int) or value is None):
            raise TypeError
        self.data[index] = value
