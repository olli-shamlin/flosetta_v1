
import os


class Config:
    SECRET_KEY = os.environ.get('ROSETTA_SECRET_KEY') or 'you-will-never-guess-ie-dev-key'
    DATA_PATH = os.environ.get('ROSETTA_DATA_PATH') or '/Users/david/Documents/pycharm-projects/flosetta_v1/data'
    # DATABASE_NAME = 'rosetta'
    # DATABASE_EXT = 'sqlite3'
    # DATABASE_PATH = f'{DATA_PATH}/{DATABASE_NAME}.{DATABASE_EXT}'
    DEBUG = True if os.environ.get('ROSETTA_DEBUG') else False
    # TODO: USE_TEST_DB can be deleted once the new store package is integrated into the app code
    USE_TEST_DB = True if os.environ.get('ROSETTA_USE_TEST_DB') else False
    TEST_MODE = True if os.environ.get('ROSETTA_TEST_MODE') else False
