

class RosettaError(Exception):
    """Generic app exception

    Attributes:
        message -- explanation of the error
    """
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
        return


class SpreadsheetError(RosettaError):

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
        return


class SpreadsheetIntegrity(SpreadsheetError):
    """Exception raised when integrity issues found in spreadsheets
    """
    def __init__(self):
        super().__init__('vocab integrity checks failed; see log for issues found')


class DatabaseError(RosettaError):

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
        return


class DatabaseExists(DatabaseError):
    """Exception raised when the database exists when it shouldn't

    Attributes:
        dbms_path -- full path to the database file
    """
    def __init__(self, dbms_path: str):
        self.message = f'Database file exists: {dbms_path}'
        super().__init__(self.message)


class QuizError(RosettaError):

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
        return


class ResultsNotSet(QuizError):

    def __init__(self):
        super(ResultsNotSet, self).__init__('quiz results has not been initialized')
