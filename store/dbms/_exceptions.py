
class DatabaseException(Exception):
    pass


class UndefinedColumnName(DatabaseException):
    def __init__(self, msg):
        self.message = f'undefined column name: {msg}'
        super().__init__(self.message)


class InvalidColumnNameType(DatabaseException):
    def __init__(self, msg):
        self.message = f'column names must be of type str: "{msg}"'
        super().__init__(self.message)


class InvalidColumnType(DatabaseException):
    def __init__(self, col_name, typ):
        self.message = f'invalid column type: "{typ}" for column {col_name}'
        super().__init__(self.message)


class InvalidTableName(DatabaseException):
    def __init__(self, table_name):
        self.message = f'"{table_name}" is a bad table name'
        super().__init__(self.message)


class TableDoesNotExist(DatabaseException):
    def __init__(self, msg):
        self.message = f'no such table: {msg}'
        super().__init__(self.message)


class IntegrityError(DatabaseException):
    def __init__(self, msg):
        self.message = msg
        super().__init__(self.message)


class InvalidRowId(DatabaseException):
    def __init__(self, table_name, row_id):
        self.message = f'no rows with an id of {row_id} exists in table {table_name}'
        super().__init__(self.message)


class RowIdNotUnique(DatabaseException):
    def __init__(self, table_name, row_id):
        self.message = f'multiple rows exist in {table_name} with row id {row_id}'
