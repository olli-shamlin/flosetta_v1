
from contextlib import closing
import sqlite3
import os
from app.model import Model
from app.model.dbms import create
from app.utils import FilePaths as files


def test_update_character():

    item = Model().alphabet.characters[100]
    for _ in range(10):
        item.statistics.increment(correct=True)

    item.update()

    cols = {
        'quizzed': item.statistics.quizzed,
        'correct': item.statistics.correct,
        'consecutive_correct': item.statistics.consecutive_correct,
        'consecutive_wrong': item.statistics.consecutive_incorrect
    }

    with sqlite3.connect(files.test_database.full_path) as conn:
        with closing(conn.cursor()) as crs:
            columns = ', '.join([c for c in cols.keys()])
            crs.execute(f'SELECT {columns} FROM kana WHERE _ROWID_ = {item.id}')
            rows = crs.fetchall()

            assert len(rows) == 1
            assert rows[0][0] == 10
            assert rows[0][1] == 10
            assert rows[0][2] == 10
            assert rows[0][3] == 0

    return


def test_update_word():

    item = Model().vocabulary.words[0]
    for _ in range(10):
        item.statistics.increment(correct=True)

    item.update()

    cols = {
        'quizzed': item.statistics.quizzed,
        'correct': item.statistics.correct,
        'consecutive_correct': item.statistics.consecutive_correct,
        'consecutive_wrong': item.statistics.consecutive_incorrect
    }

    with sqlite3.connect(files.test_database.full_path) as conn:
        with closing(conn.cursor()) as crs:
            columns = ', '.join([c for c in cols.keys()])
            crs.execute(f'SELECT {columns} FROM vocab WHERE _ROWID_ = {item.id}')
            rows = crs.fetchall()

            assert len(rows) == 1
            assert rows[0][0] == 10
            assert rows[0][1] == 10
            assert rows[0][2] == 10
            assert rows[0][3] == 0

    return


def test_vocabulary_update():

    m = Model()

    assert m.vocabulary.is_dirty is False
    assert m.alphabet.is_dirty is False
    assert m.is_dirty is False

    for i in range(len(m.vocabulary.words)):
        for j in range(i+1):
            m.vocabulary.words[i].statistics.increment(correct=True)

    assert m.vocabulary.is_dirty is True
    assert m.alphabet.is_dirty is False
    assert m.is_dirty is True

    m.vocabulary.save()

    assert m.vocabulary.is_dirty is False
    assert m.alphabet.is_dirty is False
    assert m.is_dirty is False

    columns = 'quizzed, correct, consecutive_correct, consecutive_wrong'
    answers = [[11, 11, 11, 0]] + [[i, i, i, 0] for i in range(2, 101)]

    with sqlite3.connect(files.test_database.full_path) as conn:
        with closing(conn.cursor()) as crs:
            for i, word in enumerate(m.vocabulary.words):
                # TODO remove redundant with conn/with crs statements below
                with sqlite3.connect(files.test_database.full_path) as conn:
                    with closing(conn.cursor()) as crs:
                        crs.execute(f'SELECT {columns} FROM vocab WHERE _ROWID_ = {word.id}')
                        rows = crs.fetchall()

                        assert len(rows) == 1
                        assert rows[0][0] == answers[i][0]
                        assert rows[0][1] == answers[i][1]
                        assert rows[0][2] == answers[i][2]
                        assert rows[0][3] == answers[i][3]

    return


def test_alphabet_update():

    # start with a fresh version of the test database (just to make checking the test results easier/more programatic
    if os.path.exists(files.test_database.full_path):
        os.remove(files.test_database.full_path)

    create()

    m = Model()

    assert m.vocabulary.is_dirty is False
    assert m.alphabet.is_dirty is False
    assert m.is_dirty is False

    for i in range(len(m.alphabet.characters)):
        for j in range(i+1):
            m.alphabet.characters[i].statistics.increment(correct=(i % 2 == 0))  # mark every other row as correct

    assert m.vocabulary.is_dirty is False
    assert m.alphabet.is_dirty is True
    assert m.is_dirty is True

    m.alphabet.save()

    assert m.vocabulary.is_dirty is False
    assert m.alphabet.is_dirty is False
    assert m.is_dirty is False

    columns = 'quizzed, correct, consecutive_correct, consecutive_wrong'
    with sqlite3.connect(files.test_database.full_path) as conn:
        with closing(conn.cursor()) as crs:
            for i, character in enumerate(m.alphabet.characters):
                crs.execute(f'SELECT {columns} FROM kana WHERE _ROWID_ = {character.id}')
                rows = crs.fetchall()

                assert len(rows) == 1
                if character.id % 2:  # when the character id is an odd number...
                    assert rows[0][0] == character.id
                    assert rows[0][1] == character.id
                    assert rows[0][2] == character.id
                    assert rows[0][3] == 0
                else:  # when the character id is an even number...
                    assert rows[0][0] == character.id
                    assert rows[0][1] == 0
                    assert rows[0][2] == 0
                    assert rows[0][3] == character.id

    return


def test_model_update():

    # start with a fresh version of the test database (just to make checking the test results easier/more programatic
    if os.path.exists(files.test_database.full_path):
        os.remove(files.test_database.full_path)

    create()

    m = Model()

    assert m.vocabulary.is_dirty is False
    assert m.alphabet.is_dirty is False
    assert m.is_dirty is False

    for i in range(len(m.vocabulary.words)):
        for j in range(i + 1):
            # mark every word with an odd id as correct
            m.vocabulary.words[i].statistics.increment(correct=bool(m.vocabulary.words[i].id % 2))

    for i in range(len(m.alphabet.characters)):
        for j in range(i + 1):
            # mark every word with an even id as correct
            m.alphabet.characters[i].statistics.increment(correct=bool(m.alphabet.characters[i].id % 2))

    assert m.vocabulary.is_dirty is True
    assert m.alphabet.is_dirty is True
    assert m.is_dirty is True

    m.save()

    assert m.vocabulary.is_dirty is False
    assert m.alphabet.is_dirty is False
    assert m.is_dirty is False

    columns = 'quizzed, correct, consecutive_correct, consecutive_wrong'
    with sqlite3.connect(files.test_database.full_path) as conn:
        with closing(conn.cursor()) as crs:

            for i, word in enumerate(m.vocabulary.words):

                crs.execute(f'SELECT {columns} FROM kana WHERE _ROWID_ = {word.id}')
                rows = crs.fetchall()

                assert len(rows) == 1
                if word.id % 2:  # when the word's id is an odd number...
                    assert rows[0][0] == word.id
                    assert rows[0][1] == word.id
                    assert rows[0][2] == word.id
                    assert rows[0][3] == 0
                else:  # when the word's id is an even number...
                    assert rows[0][0] == word.id
                    assert rows[0][1] == 0
                    assert rows[0][2] == 0
                    assert rows[0][3] == word.id

            for i, character in enumerate(m.alphabet.characters):
                crs.execute(f'SELECT {columns} FROM kana WHERE _ROWID_ = {character.id}')
                rows = crs.fetchall()

                assert len(rows) == 1
                if character.id % 2:  # when the character id is an odd number...
                    assert rows[0][0] == character.id
                    assert rows[0][1] == character.id
                    assert rows[0][2] == character.id
                    assert rows[0][3] == 0
                else:  # when the character id is an even number...
                    assert rows[0][0] == character.id
                    assert rows[0][1] == 0
                    assert rows[0][2] == 0
                    assert rows[0][3] == character.id

    return
