
import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess-ie-dev-key'
    DATA_PATH = 'app/data'
    DATABASE_NAME = 'rosetta'
    DATABASE_EXT = 'sqlite3'
    DATABASE_PATH = f'{DATA_PATH}/{DATABASE_NAME}.{DATABASE_EXT}'
    DEBUG = True
    USE_TEST_DB = True if os.environ.get('ROSETTA_USE_TEST_DB') else False
