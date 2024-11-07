
from contextlib import closing
import sqlite3
import os
from app.model import Model
from app.model.dbms import create
from app.utils import FilePaths as files

_NUM_CHARACTERS = 107
_NUM_WORDS = 100
_NUM_UPDATES = 5


def test_update_character():

    m = Model()

    for character in m.syllabary:
        for _ in range(_NUM_UPDATES):
            character.statistics.increment(correct=(True if character.id < 51 else False))
        character.update()

    columns = 'quizzed, correct, consecutive_correct, consecutive_wrong'

    with sqlite3.connect(files.test_database.full_path) as conn:
        with closing(conn.cursor()) as crs:
            for character in m.syllabary:
                crs.execute(f'SELECT {columns} FROM kana WHERE _ROWID_ = {character.id}')
                rows = crs.fetchall()

                assert len(rows) == 1
                if character.id < 51:
                    assert rows[0][0] == _NUM_UPDATES
                    assert rows[0][1] == _NUM_UPDATES
                    assert rows[0][2] == _NUM_UPDATES
                    assert rows[0][3] == 0
                else:
                    assert rows[0][0] == _NUM_UPDATES
                    assert rows[0][1] == 0
                    assert rows[0][2] == 0
                    assert rows[0][3] == _NUM_UPDATES

    return


def test_update_word():

    m = Model()

    for word in m.vocabulary:
        for _ in range(_NUM_UPDATES):
            word.statistics.increment(correct=(True if word.id < 51 else False))
        word.update()

    columns = 'quizzed, correct, consecutive_correct, consecutive_wrong'

    with sqlite3.connect(files.test_database.full_path) as conn:
        with closing(conn.cursor()) as crs:
            for word in m.vocabulary:
                crs.execute(f'SELECT {columns} FROM vocab WHERE _ROWID_ = {word.id}')
                rows = crs.fetchall()

                assert len(rows) == 1
                if word.id < 51:
                    assert rows[0][0] == _NUM_UPDATES
                    assert rows[0][1] == _NUM_UPDATES
                    assert rows[0][2] == _NUM_UPDATES
                    assert rows[0][3] == 0
                else:
                    assert rows[0][0] == _NUM_UPDATES
                    assert rows[0][1] == 0
                    assert rows[0][2] == 0
                    assert rows[0][3] == _NUM_UPDATES

    return


def test_vocabulary_update():

    m = Model()

    assert m.vocabulary.is_dirty is False
    assert m.syllabary.is_dirty is False
    assert m.is_dirty is False

    for w in m.vocabulary:
        for _ in range(_NUM_UPDATES):
            w.statistics.increment(correct=(True if w.id < 51 else False))

    assert m.vocabulary.is_dirty is True
    assert m.syllabary.is_dirty is False
    assert m.is_dirty is True

    m.vocabulary.save()

    assert m.vocabulary.is_dirty is False
    assert m.syllabary.is_dirty is False
    assert m.is_dirty is False

    columns = 'quizzed, correct, consecutive_correct, consecutive_wrong'

    with sqlite3.connect(files.test_database.full_path) as conn:
        with closing(conn.cursor()) as crs:
            for i, word in enumerate(m.vocabulary):
                # TODO remove redundant with conn/with crs statements below
                with sqlite3.connect(files.test_database.full_path) as conn:
                    with closing(conn.cursor()) as crs:
                        crs.execute(f'SELECT {columns} FROM vocab WHERE _ROWID_ = {word.id}')
                        rows = crs.fetchall()

                        assert len(rows) == 1
                        if word.id < 51:
                            assert rows[0][0] == _NUM_UPDATES * 2
                            assert rows[0][1] == _NUM_UPDATES * 2
                            assert rows[0][2] == _NUM_UPDATES * 2
                            assert rows[0][3] == 0
                        else:
                            assert rows[0][0] == _NUM_UPDATES * 2
                            assert rows[0][1] == 0
                            assert rows[0][2] == 0
                            assert rows[0][3] == _NUM_UPDATES * 2

    return


def test_alphabet_update():

    m = Model()

    assert m.vocabulary.is_dirty is False
    assert m.syllabary.is_dirty is False
    assert m.is_dirty is False

    for character in m.syllabary:
        for _ in range(_NUM_UPDATES):
            character.statistics.increment(correct=(True if character.id < 51 else False))

    assert m.vocabulary.is_dirty is False
    assert m.syllabary.is_dirty is True
    assert m.is_dirty is True

    m.syllabary.save()

    assert m.vocabulary.is_dirty is False
    assert m.syllabary.is_dirty is False
    assert m.is_dirty is False

    columns = 'quizzed, correct, consecutive_correct, consecutive_wrong'
    ea = _NUM_UPDATES * 2
    answers = [([ea, ea, ea, 0] if c.id < 51 else [ea, 0, 0, ea]) for c in m.syllabary]

    with sqlite3.connect(files.test_database.full_path) as conn:
        with closing(conn.cursor()) as crs:
            for i, character in enumerate(m.syllabary):
                # TODO remove redundant with conn/with crs statements below
                with sqlite3.connect(files.test_database.full_path) as conn:
                    with closing(conn.cursor()) as crs:
                        crs.execute(f'SELECT {columns} FROM kana WHERE _ROWID_ = {character.id}')
                        rows = crs.fetchall()

                        assert len(rows) == 1
                        assert rows[0][0] == answers[i][0]
                        assert rows[0][1] == answers[i][1]
                        assert rows[0][2] == answers[i][2]
                        assert rows[0][3] == answers[i][3]

    return


def test_model_update():

    m = Model()

    assert m.vocabulary.is_dirty is False
    assert m.syllabary.is_dirty is False
    assert m.is_dirty is False

    for w in m.vocabulary:
        for _ in range(_NUM_UPDATES):
            w.statistics.increment(correct=(True if w.id < 51 else False))

    for c in m.syllabary:
        for _ in range(_NUM_UPDATES):
            c.statistics.increment(correct=(True if c.id < 51 else False))

    assert m.vocabulary.is_dirty is True
    assert m.syllabary.is_dirty is True
    assert m.is_dirty is True

    m.save()

    assert m.vocabulary.is_dirty is False
    assert m.syllabary.is_dirty is False
    assert m.is_dirty is False

    columns = 'quizzed, correct, consecutive_correct, consecutive_wrong'
    with sqlite3.connect(files.test_database.full_path) as conn:
        with closing(conn.cursor()) as crs:

            for word in m.vocabulary:

                crs.execute(f'SELECT {columns} FROM vocab WHERE _ROWID_ = {word.id}')
                rows = crs.fetchall()

                assert len(rows) == 1
                if word.id < 51:
                    assert rows[0][0] == _NUM_UPDATES * 3
                    assert rows[0][1] == _NUM_UPDATES * 3
                    assert rows[0][2] == _NUM_UPDATES * 3
                    assert rows[0][3] == 0
                else:
                    assert rows[0][0] == _NUM_UPDATES * 3
                    assert rows[0][1] == 0
                    assert rows[0][2] == 0
                    assert rows[0][3] == _NUM_UPDATES * 3

            for character in m.syllabary:

                crs.execute(f'SELECT {columns} FROM kana WHERE _ROWID_ = {character.id}')
                rows = crs.fetchall()

                assert len(rows) == 1
                if character.id < 51:
                    assert rows[0][0] == _NUM_UPDATES * 3
                    assert rows[0][1] == _NUM_UPDATES * 3
                    assert rows[0][2] == _NUM_UPDATES * 3
                    assert rows[0][3] == 0
                else:
                    assert rows[0][0] == _NUM_UPDATES * 3
                    assert rows[0][1] == 0
                    assert rows[0][2] == 0
                    assert rows[0][3] == _NUM_UPDATES * 3

    return
