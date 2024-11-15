
from conftest import CursorContextManager
from store import create_tables
from store import populate_tables
from store import update_database
from store._data_files import DataFiles as _files
from typing import Optional


def test_store_create_tables():

    create_tables()

    with CursorContextManager() as crs:
        # Confirm the database now contains the expected tables
        crs.execute('SELECT name FROM sqlite_schema WHERE type = "table" AND name NOT LIKE "sqlite_%"')
        rows = crs.fetchall()
        rows = [r[0] for r in rows]

        assert len(rows) == 8
        assert 'vocab' in rows
        assert 'vocab_notes' in rows
        assert 'vocab_tags' in rows
        assert 'kana' in rows
        assert 'kana_notes' in rows

        # Confirm each table's schema is as expected
        crs.execute("SELECT sql FROM sqlite_schema WHERE name = 'vocab'")
        rows = crs.fetchall()
        assert len(rows) == 1 and len(rows[0]) == 1
        assert rows[0][0] == 'CREATE TABLE vocab (english_w TEXT, romaji_w TEXT, kana_w TEXT NOT NULL UNIQUE, ' \
                             'kanji_w TEXT, part_of_speech TEXT, quizzed INTEGER, correct INTEGER, ' \
                             'consecutive_correct INTEGER, consecutive_incorrect INTEGER)'

        crs.execute("SELECT sql FROM sqlite_schema WHERE name = 'vocab_notes'")
        rows = crs.fetchall()
        assert len(rows) == 1 and len(rows[0]) == 1
        assert rows[0][0] == 'CREATE TABLE vocab_notes (word_id INTEGER, note TEXT)'

        crs.execute("SELECT sql FROM sqlite_schema WHERE name = 'vocab_tags'")
        rows = crs.fetchall()
        assert len(rows) == 1 and len(rows[0]) == 1
        assert rows[0][0] == 'CREATE TABLE vocab_tags (word_id INTEGER, tag TEXT)'

        crs.execute("SELECT sql FROM sqlite_schema WHERE name = 'kana'")
        rows = crs.fetchall()
        assert len(rows) == 1 and len(rows[0]) == 1
        assert rows[0][0] == 'CREATE TABLE kana (romaji TEXT NOT NULL UNIQUE, hiragana TEXT, katakana TEXT, ' \
                             'category TEXT, quizzed INTEGER, correct INTEGER, consecutive_correct INTEGER, ' \
                             'consecutive_incorrect INTEGER)'

        crs.execute("SELECT sql FROM sqlite_schema WHERE name = 'kana_notes'")
        rows = crs.fetchall()
        assert len(rows) == 1 and len(rows[0]) == 1
        assert rows[0][0] == 'CREATE TABLE kana_notes (kana_id INTEGER, katakana_note TEXT, hiragana_note TEXT)'

    return


def test_populate_tables():

    populate_tables()

    with CursorContextManager() as crs:
        # Spot check vocab tables (more thorough testing done in test_verify_vocab_tables())
        crs.execute('SELECT COUNT(*) FROM vocab')
        rows = crs.fetchall()
        assert rows[0][0] == 100
        crs.execute('SELECT COUNT(*) FROM vocab_notes')
        rows = crs.fetchall()
        assert rows[0][0] == 67
        crs.execute('SELECT COUNT(*) FROM vocab_tags')
        rows = crs.fetchall()
        assert rows[0][0] == 150

        # Spot check kana tables (more through testing done in test_verify_kana_tables())
        crs.execute('SELECT COUNT(*) FROM kana')
        rows = crs.fetchall()
        assert rows[0][0] == 107
        crs.execute('SELECT COUNT(*) FROM kana WHERE category = "Basic"')
        rows = crs.fetchall()
        assert rows[0][0] == 46
        crs.execute('SELECT COUNT(*) FROM kana WHERE category = "Dakuten"')
        rows = crs.fetchall()
        assert rows[0][0] == 25
        crs.execute('SELECT COUNT(*) FROM kana WHERE category = "Modified YA"')
        rows = crs.fetchall()
        assert rows[0][0] == 12
        crs.execute('SELECT COUNT(*) FROM kana WHERE category = "Modified YO"')
        rows = crs.fetchall()
        assert rows[0][0] == 12
        crs.execute('SELECT COUNT(*) FROM kana WHERE category = "Modified YU"')
        rows = crs.fetchall()
        assert rows[0][0] == 12
        crs.execute('SELECT COUNT(*) FROM kana_notes')
        rows = crs.fetchall()
        assert rows[0][0] == 45

    return


def test_verify_vocab_tables():

    with CursorContextManager() as crs:
        crs.execute(f'SELECT _ROWID_, * from vocab')
        vocab_rows = crs.fetchall()
        crs.execute(f'SELECT * from vocab_notes')
        vocab_notes_rows = crs.fetchall()
        crs.execute(f'SELECT * from vocab_tags')
        vocab_tag_rows = crs.fetchall()

    assert len(vocab_rows) == 100
    assert len(vocab_notes_rows) == 67
    assert len(vocab_tag_rows) == 150

    # Assure rows in "vocab" are as expected
    for i, row in enumerate(vocab_rows):
        pos = ['pos-a', 'pos-b', 'pos-c', 'pos-d', None][i % 5]
        i += 1
        assert row[1:] == (f'english {i}', f'romaji {i}', f'kana {i}', f'kanji {i}', pos, 0, 0, 0, 0)

    # Assure rows in "vocab_notes" are as expected
    note_map = {r[0]: r[1] for r in vocab_notes_rows}
    for row in vocab_rows:
        word_idx = int(str(row[1]).split(' ')[-1])
        if word_idx % 3:
            assert note_map[row[0]] == f'note {word_idx}'
        else:
            assert row[0] not in note_map.keys()

    # Assure rows in "vocab_tags" are as expected
    with CursorContextManager() as crs:
        for row in vocab_rows:
            word_idx = int(str(row[1]).split(' ')[-1])
            m = word_idx % 4
            if m:
                crs.execute(f'SELECT * FROM vocab_tags WHERE word_id = {row[0]}')
                rows = crs.fetchall()
                assert len(rows) == m
                expected = [f'tag-{"abc"[i]}' for i in range(m)]
                in_database = [r[1] for r in rows]
                assert set(expected) == set(in_database)

    return


def test_verify_kana_tables():

    def check_basic_kana(target_romaji, expected_hira, expected_kata, expected_hira_note, expected_kata_note):
        with CursorContextManager() as crs:
            crs.execute(f'SELECT _ROWID_, * FROM kana WHERE romaji = "{target_romaji}"')
            roes = crs.fetchall()
            row_id = roes[0][0]
            assert len(roes) == 1 and \
                   roes[0] == (row_id, target_romaji, expected_hira, expected_kata, 'Basic', 0, 0, 0, 0)
            crs.execute(f'SELECT hiragana_note, katakana_note FROM kana_notes WHERE kana_id = {row_id}')
            roes = crs.fetchall()
            assert len(roes) == 1 and roes[0] == (expected_kata_note, expected_hira_note)
            return

    def check_other_kana(target_romaji, expected_hira, expected_kata, expected_cat):
        with CursorContextManager() as crs:
            crs.execute(f'SELECT _ROWID_, * FROM kana WHERE romaji = "{target_romaji}"')
            roes = crs.fetchall()
            row_id = roes[0][0]
            assert len(roes) == 1 and \
                   roes[0] == (row_id, target_romaji, expected_hira, expected_kata, expected_cat, 0, 0, 0, 0)
            return

    # Spot check some rows in the kana table

    check_basic_kana('a', 'あ', 'ア',
                     'Ah! You found the letter A. Look for the letter A.',
                     'Ark. Think of Noah’s Ark.')
    check_basic_kana('ka', 'か', 'カ',
                     'Batman will never Katch the Jo-KA! Think of Batman punching the Joker’s face. KA-POW!',
                     'Batman will never Katch the Jo-KA! Think of the Joker’s face.')
    check_basic_kana('shi', 'し', 'シ',
                     'Shi has shiny hair. Think of a girl with long hair.',
                     'Shi-tsu dogs. Shi is the girl and looks to the right. Tsu is the boy and looks to the left.')
    check_basic_kana('tsu', 'つ', 'ツ',
                     'Tsunami! Imagine a giant tsunami wave.',
                     'Tsu promises Shi a tsunami of kisses. Now he has both eyes wide open in anticipation.')
    check_basic_kana('no', 'の', 'ノ',
                     'No Smoking! Think of a no smoking sign.',
                     'NO? Shi said “no”! Tsu closes his eyes in sorrow. Now he has NO eyes.')
    check_basic_kana('mi', 'み', 'ミ',
                     'Meep meep! Think of a roadrunner',
                     'Mi has three meaty lines. Think of it was a progression from Ni which has two neat lines…'
                     'DO RE MI')
    check_basic_kana('yu', 'ゆ', 'ユ',
                     'Yuck! Fish again? Imagine a smelly fish on a plate.',
                     'You’re number 1. This symbol looks like the number 1.')
    check_basic_kana('re', 'れ', 'レ',
                     'Reptiles are really repulsive. Think of a snake.',
                     'Hoo-REY for Ray. He’s broken free! And he took the leg with him as he bounces away.')
    check_basic_kana('wo', 'を', 'ヲ',
                     'Whoa! Watch your step. Think of a man about to walk on a frozen lake.',
                     'Bow and Arrow. Despite being written as WO it is pronounced ‘O’')
    check_other_kana('ga', 'が', 'ガ', 'Dakuten')
    check_other_kana('ze', 'ぜ', 'ゼ', 'Dakuten')
    check_other_kana('dzi', 'ぢ', 'ヂ', 'Dakuten')
    check_other_kana('pi', 'ぴ', 'ピ', 'Dakuten')
    check_other_kana('kya', 'きゃ', 'キャ', 'Modified YA')
    check_other_kana('hya', 'ひゃ', 'ヒャ', 'Modified YA')
    check_other_kana('gyo', 'ぎょ', 'ギョ', 'Modified YO')
    check_other_kana('cho', 'ちょ', 'チョ', 'Modified YO')
    check_other_kana('jyu', 'じゅ', 'ジュ', 'Modified YU')
    check_other_kana('byu', 'びゅ', 'ビュ', 'Modified YU')

    return


def _get_rowid(kana: str) -> int:

    with CursorContextManager() as crs:
        crs.execute(f'SELECT _ROWID_ FROM vocab WHERE kana_w ="{kana}"')
        rows = crs.fetchall()

    assert len(rows) == 1
    return rows[0][0]


class _AddedRowIds:
    kana_33: None
    kana_45: None
    kana_69: None


def test_update_database():

    # To test updating the database, replace the value in the vocab_spreadsheet "slot" of the DataFiles
    # to the fully qualified path name to the test spreadsheet for database updates. We save the original
    # path to put it back in the DataFiles "slot" when the test is done.
    original_vocab_spreadsheet_file = _files.vocab_spreadsheet
    path = '/'.join(original_vocab_spreadsheet_file.split('/')[:-1])
    _files.vocab_spreadsheet = f'{path}/test_vocabulary_update.numbers'

    # We need to get the row ids of the words that will get deleted from the database during this test.
    # We will need to use them to verify the associated notes and tags got deleted from the vocab_notes and
    # vocab_tags tables.
    _AddedRowIds.kana_33 = _get_rowid('kana 33')
    _AddedRowIds.kana_45 = _get_rowid('kana 45')
    _AddedRowIds.kana_69 = _get_rowid('kana 69')

    update_database()

    # Assure that the database tables have the expected number of rows after the update
    # Note further verification checks are done in the test_update_database_verify_* test functions below.
    with CursorContextManager() as crs:
        crs.execute('SELECT COUNT(*) FROM vocab')
        rows = crs.fetchall()
        num_rows_in_vocab = rows[0][0]

        crs.execute('SELECT COUNT(*) FROM vocab_notes')
        rows = crs.fetchall()
        num_rows_in_vocab_notes = rows[0][0]

        crs.execute('SELECT COUNT(*) FROM vocab_tags')
        rows = crs.fetchall()
        num_rows_in_vocab_tags = rows[0][0]

    assert num_rows_in_vocab == 100
    assert num_rows_in_vocab_notes == 68
    assert num_rows_in_vocab_tags == 150

    # Put the original fully qualified test_vocabulary spreadsheet back in its DataFiles "slot"
    _files.vocab_spreadsheet = original_vocab_spreadsheet_file

    return


def _verify_deletion(kana: str, word_id: int) -> bool:

    with CursorContextManager() as crs:
        crs.execute(f'SELECT * FROM vocab WHERE kana_w = "{kana}"')
        rows = crs.fetchall()
        vocab_record_deleted = len(rows) == 0

        crs.execute(f'SELECT * FROM vocab_notes WHERE word_id = {word_id}')
        rows = crs.fetchall()
        notes_record_deleted = len(rows) == 0

        crs.execute(f'SELECT * FROM vocab_tags WHERE word_id= {word_id}')
        rows = crs.fetchall()
        tag_records_deleted = len(rows) == 0

    return vocab_record_deleted and notes_record_deleted and tag_records_deleted


def test_update_database_verify_delete():

    # Assure words removed from the spreadsheet are no longer in the database.
    assert _AddedRowIds.kana_33 and _AddedRowIds.kana_45 and _AddedRowIds.kana_69
    assert _verify_deletion('kana 33', _AddedRowIds.kana_33)
    _AddedRowIds.kana_33 = None
    assert _verify_deletion('kana 45', _AddedRowIds.kana_45)
    _AddedRowIds.kana_45 = None
    assert _verify_deletion('kana 69', _AddedRowIds.kana_69)
    _AddedRowIds.kana_69 = None

    return


def _verify_changed_row(expected_vocab: list,
                        expected_note: Optional[str],
                        expected_tags: Optional[list[str]]) -> bool:

    with CursorContextManager() as crs:
        kana = expected_vocab[2]
        crs.execute(f'SELECT _ROWID_, * FROM vocab WHERE kana_w = "{kana}"')
        rows = crs.fetchall()
        assert len(rows) == 1
        word_id = rows[0][0]
        if rows[0][1] != expected_vocab[0]:
            return False
        if rows[0][2] != expected_vocab[1]:
            return False
        if rows[0][3] != expected_vocab[2]:
            return False
        if rows[0][4] != expected_vocab[3]:
            return False
        if rows[0][5] != expected_vocab[4]:
            return False
        if (rows[0][6] != 0) or (rows[0][7] != 0) or (rows[0][8] != 0) or (rows[0][9] != 0):
            return False

        crs.execute(f'SELECT * FROM vocab_notes WHERE word_id = {word_id}')
        rows = crs.fetchall()
        note_ok = (rows[0][1] == expected_note) if expected_note else (len(rows) == 0)
        if not note_ok:
            return False

        crs.execute(f'SELECT * FROM vocab_tags WHERE word_id = {word_id}')
        rows = crs.fetchall()
        if expected_tags:
            for i, expected_tag in enumerate(expected_tags):
                if expected_tag != rows[i][1]:
                    return False
        else:
            if len(rows) != 0:
                return False

    return True


def test_update_database_verify_add():

    # Assure new words in the spreadsheet are now in the database too.
    assert _verify_changed_row(['NEW ENGLISH 1', 'NEW ROMAJI 1', 'NEW KANA 1', 'NEW KANJI 1', 'NEW-POS-1', 0, 0, 0, 0],
                               expected_note=None, expected_tags=None)
    assert _verify_changed_row(['NEW ENGLISH 2', 'NEW ROMAJI 2', 'NEW KANA 2', 'NEW KANJI 2', None, 0, 0, 0, 0],
                               expected_note='NEW NOTE 2', expected_tags=None)
    assert _verify_changed_row(['NEW ENGLISH 3', 'NEW ROMAJI 3', 'NEW KANA 3', 'NEW KANJI 3', None, 0, 0, 0, 0],
                               expected_note=None, expected_tags=['NEW-TAG-A', 'NEW-TAG-B'])

    return


def test_update_database_verify_update():

    # Assure words changed in the spreadsheet have been updated in the database.
    assert _verify_changed_row(['english 10', 'romaji 10', 'kana 10', 'kanji 10', None, 0, 0, 0, 0],
                               expected_note='NOTE 10 UPDATED', expected_tags=['tag-a', 'tag-b'])
    assert _verify_changed_row(['english 25', 'romaji 25', 'kana 25', 'kanji 25', None, 0, 0, 0, 0],
                               expected_note='NOTE 25 UPDATED', expected_tags=['tag-a'])
    assert _verify_changed_row(['ENGLISH 38 UPDATED', 'ROMAJI 38 UPDATED', 'kana 38', 'KANJI 38 UPDATED', 'Pos-b',
                                0, 0, 0, 0],
                               expected_note='EVERY CELL ON THIS LINE CHANGED',
                               expected_tags=['tag-b', 'tag-c', 'tag-d'])
    assert _verify_changed_row(['ENGLISH 46 UPDATED', 'ROMAJI 46 UPDATED', 'kana 46', 'KANJI 46 UPDATED', 'pos-a',
                                0, 0, 0, 0],
                               expected_note='note 46', expected_tags=['tag-a', 'tag-b'])
    assert _verify_changed_row(['english 51', 'romaji 51', 'kana 51', 'kanji 51', 'pos-a', 0, 0, 0, 0],
                               expected_note=None, expected_tags=['tag-a', 'tag-c'])
    assert _verify_changed_row(['english 65', 'romaji 65', 'kana 65', 'kanji 65', None, 0, 0, 0, 0],
                               expected_note='note 65', expected_tags=['tag-a', 'NEW-TAG-1'])
    assert _verify_changed_row(['ENGLISH 76 UPDATED', 'ROMAJI 76 UPDATED', 'kana 76', 'KANJI 76 UPDATED', 'quark',
                                0, 0, 0, 0],
                               expected_note='note 76', expected_tags=None)
    assert _verify_changed_row(['ENGLISH 92 UPDATED', 'ROMAJI 92 UPDATED', 'kana 92', 'KANJI 92 UPDATED', 'Pos-c',
                                0, 0, 0, 0],
                               expected_note='note 92', expected_tags=None)

    return
