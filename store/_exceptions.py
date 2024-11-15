
from app import FlosettaException


class StoreException(FlosettaException):
    def __init__(self, msg):
        self.message = f'flosetta.dbms.store error: {msg}'
        super().__init__(msg)
