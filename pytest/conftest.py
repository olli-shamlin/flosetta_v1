
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
        'test_mcq_vocab',
        'test_mcq_kana',
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

    sql_null = None
    stat_vals = [0, 0, 0, 0]
    rows = list()

    for i in range(1, 101):
        note = f'W{i} note' if i % 2 else sql_null
        num_tags = i % 4
        tags = '; '.join([f'W{i}T{j}' for j in range(1, num_tags+1)]) if num_tags else sql_null
        next_row = [f'W{i} english', f'W{i} romaji', f'W{i} kana', f'W{i} kanji', f'W{i} pos', note, tags]
        next_row.extend(stat_vals)
        rows.append(next_row)

    return rows

