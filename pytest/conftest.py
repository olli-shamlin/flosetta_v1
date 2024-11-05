
import os
import pytest
from app.utils import FilePaths as files
from app.model.dbms import create


def pytest_collection_modifyitems(session, config, items):
    """The following function fixes the order in which tests are run which is needed in this test suite
       since some tests modify word/character statistics that other tests will reference.
    """
    function_order = [
        'test_tables',
        'test_kana_schema',
        'test_vocab_schema',
        'test_kana_rows',
        'test_vocab_rows',
        'test_alphabet_read',
        'test_words_read',
        'test_model_vocabulary_read',
        'test_model_alphabet_read',
        'test_statistic',
        'test_statistics_word',
        'test_statistics_character',
        'test_update_character',
        'test_update_word',
        'test_vocabulary_update',
        'test_alphabet_update',
        'test_model_update',
    ]

    function_mapping = {item.name: item for item in items}
    sorted_items = [function_mapping[fn] for fn in function_order]
    items[:] = sorted_items

    return


@pytest.fixture(scope='session', autouse=True)
def create_db():
    """This fixture recreates the database before any/all tests are run.
    """

    if os.path.exists(files.test_database.full_path):
        os.remove(files.test_database.full_path)

    create()

    return


@pytest.fixture()
def expected_vocab_rows():

    return [
        ['W1 english',  'W1 romaji',  'W1 kana',  'W1 kanji',  'W1 pos',  'W1 note',  'W1T1',            0, 0, 0, 0],
        ['W2 english',  'W2 romaji',  'W2 kana',  'W2 kanji',  'W2 pos',  None,      'W2T1; W2T2',       0, 0, 0, 0],
        ['W3 english',  'W3 romaji',  'W3 kana',  'W3 kanji',  'W3 pos',  'W3 note', 'W3T1; W3T2; W3T3', 0, 0, 0, 0],
        ['W4 english',  'W4 romaji',  'W4 kana',  'W4 kanji',  'W4 pos',  None,      None,               0, 0, 0, 0],
        ['W5 english',  'W5 romaji',  'W5 kana',  'W5 kanji',  'W5 pos',  'W5 note', 'W5T1',             0, 0, 0, 0],
        ['W6 english',  'W6 romaji',  'W6 kana',  'W6 kanji',  'W6 pos',  None,      'W6T1; W6T2',       0, 0, 0, 0],
        ['W7 english',  'W7 romaji',  'W7 kana',  'W7 kanji',  'W7 pos',  'W7 note', 'W7T1; W7T2; W7T3', 0, 0, 0, 0],
        ['W8 english',  'W8 romaji',  'W8 kana',  'W8 kanji',  'W8 pos',  None,      None,               0, 0, 0, 0],
        ['W9 english',  'W9 romaji',  'W9 kana',  'W9 kanji',  'W9 pos',  'W9 note', 'W9T1',             0, 0, 0, 0],
        ['W10 english', 'W10 romaji', 'W10 kana', 'W10 kanji', 'W10 pos', None, 'W10T1; W10T2', 0, 0, 0, 0],
    ]

