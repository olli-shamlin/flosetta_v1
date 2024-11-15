
from flask import Flask
from flask_bootstrap import Bootstrap5
from config import Config


class FlosettaException(Exception):
    def __init__(self, msg):
        self.message = f'flosetta.dbms.store error: {msg}'
        super().__init__(msg)


app = Flask(__name__)
bootstrap = Bootstrap5(app)
app.config.from_object(Config)

from app import routes
