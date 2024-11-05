
import sqlite3
from app.utils import FilePaths as files
from contextlib import closing


def test_tables():

    with sqlite3.connect(files.test_database.full_path) as conn:
        with closing(conn.cursor()) as csr:

            # Do we have the expected set of tables and only the expected set of tables?
            csr.execute('SELECT name FROM sqlite_schema WHERE type = "table" AND name NOT LIKE "sqlite_%"')
            rows = csr.fetchall()
            assert len(rows) == 2
            assert rows[0][0] in ['kana', 'vocab']
            assert rows[1][0] in ['kana', 'vocab']

    return


def test_kana_schema():

    with sqlite3.connect(files.test_database.full_path) as conn:
        with closing(conn.cursor()) as csr:

            # is table's schema as expected?
            schema = 'CREATE TABLE kana (romaji TEXT, hiragana TEXT, hiragana_mnemonic TEXT, katakana TEXT, ' \
                     'katakana_mnemonic, category TEXT, quizzed INTEGER, correct INTEGER, consecutive_correct INTEGER, ' \
                     'consecutive_wrong INTEGER)'
            csr.execute('SELECT sql FROM sqlite_schema WHERE name = "kana"')
            row = csr.fetchone()
            assert row[0] == schema

    return


def test_vocab_schema():

    with sqlite3.connect(files.test_database.full_path) as conn:
        with closing(conn.cursor()) as csr:

            schema = 'CREATE TABLE vocab (english_w TEXT, romaji_w TEXT, kana_w TEXT, kanji_w TEXT, pos TEXT, ' \
                     'note TEXT, tag TEXT, quizzed INTEGER, correct INTEGER, consecutive_correct INTEGER, ' \
                     'consecutive_wrong INTEGER)'
            csr.execute('SELECT sql FROM sqlite_schema WHERE name = "vocab"')
            row = csr.fetchone()
            assert row[0] == schema

    return


def test_vocab_rows(expected_vocab_rows):

    answers = sorted(expected_vocab_rows, key=lambda e: e[0])

    with sqlite3.connect(files.test_database.full_path) as conn:
        with closing(conn.cursor()) as crs:
            crs.execute('SELECT * FROM vocab ORDER BY english_w')
            rows = crs.fetchall()

    assert len(rows) == len(answers)

    for i, row in enumerate(rows):
        for j, col in enumerate(row):
            assert col == answers[i][j]

    return


def test_kana_rows():

    answers = [
        ['chi', 'ち', 'Five chirping chicks. Look for the number 5.',
         'チ', 'Nacho the Chili Pepper. Think of a long chinned cheerful chili pepper with a sombrero.',
         'Basic', 0, 0, 0, 0],
        ['dzyu', 'ぢゅ', None, 'ヂュ', None, 'Modified YU', 0, 0, 0, 0],
        ['e', 'え', 'Ed the pelican. He makes an ‘eh’ sound.', 'エ', 'Egg Timer. An egg timer keeps the time eggsactly.',
         'Basic', 0, 0, 0, 0],
        ['mi', 'み', 'Meep meep! Think of a roadrunner',
         'ミ', 'Mi has three meaty lines. Think of it was a progression from Ni which has two neat lines…DO RE MI',
         'Basic', 0, 0, 0, 0],
        ['n/m', 'ん', None, 'ン', None, 'Basic', 0, 0, 0, 0],
        ['pi', 'ぴ', None, 'ピ', None, 'Dakuten', 0, 0, 0, 0],
        ['pya', 'ぴゃ', None, 'ピャ', None, 'Modified YA', 0, 0, 0, 0],
        ['ryo', 'りよ', None, 'リョ', None, 'Modified YO', 0, 0, 0, 0],
        ['su', 'す', 'Super Sumo! Imagine a caped superman sumo swooping into action.',
         'ス', 'Sue the nurse is late for surgery. Think of Sue running at full speed through a hospital.',
         'Basic', 0, 0, 0, 0],
        ['zu', 'ず', None, 'ズ', None, 'Dakuten', 0, 0, 0, 0],
    ]

    with sqlite3.connect(files.test_database.full_path) as conn:
        with closing(conn.cursor()) as crs:
            crs.execute('SELECT * FROM kana '
                        'WHERE romaji IN ("ryo", "zu", "su", "dzyu", "pya", "pi", "e", "n/m", "mi", "chi") '
                        'ORDER BY romaji')
            rows = crs.fetchall()

    assert len(rows) == len(answers)

    for i, row in enumerate(rows):
        for j, col in enumerate(row):
            assert col == answers[i][j]

    return
