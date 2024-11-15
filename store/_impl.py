
import os
from glob import glob
import datetime
import shutil

from app import app
from app.utils.exceptions import RosettaError
import store.dbms as _dbms
from ._schema import TABLE_SCHEMAS as _TABLE_SCHEMAS
from ._schema import QUIZ_METRIC_COLUMNS as _QUIZ_METRIC_COLUMNS
from ._types import VocabWorkbook as _VocabWorkbook
from ._types import KanaWorkbook as _KanaWorkbook
from ._types import VocabDatabase as _VocabDatabase
from ._types import DatabaseWordRecord as _DatabaseWordRecord
from ._types import VocabWorkbookRecord as _VocabWorkbookRecord
_NUM_BACKUP_COPIES = 2  # set this variable to one less than the desired number of backups to keep around
_quiz_metric_values = [0, 0, 0, 0]


def _now() -> str:
    return datetime.datetime.now().strftime('%Y%m%d.%H%M%S.%f')


def _backup():

    # confirm the data directory exists
    if 'DATA_PATH' not in app.config.keys():
        raise RosettaError('DATA_PATH not set in app config')
    if not os.path.exists(app.config['DATA_PATH']):
        raise FileNotFoundError(f'data directory does not exist: {app.config["DATA_PATH"]}')

    # create the backup directory if it doesn't exist
    backup_path = f'{app.config["DATA_PATH"]}/backups'
    if not os.path.exists(backup_path):
        os.makedirs(backup_path)

    now = _now()
    files_to_backup = glob(f'{app.config["DATA_PATH"]}/*.sqlite3') + glob(f'{app.config["DATA_PATH"]}/*.numbers')

    for next_file in files_to_backup:

        # How many versions of this file do we have in the backup directory?.
        next_file_name = next_file.split('/')[-1]
        next_file_extension = next_file_name.split('.')[-1]
        next_file_name = next_file_name.split('.')[0]
        existing_backups = glob(f'{backup_path}/{next_file_name}-*.{next_file_extension}')
        if len(existing_backups) > _NUM_BACKUP_COPIES:
            # We only want to keep three backup copies of a file; delete the oldest one.
            oldest_backup = sorted(existing_backups)[0]
            os.remove(oldest_backup)

        # now make the backup copy
        backup_file = f'{backup_path}/{next_file_name}-{now}.{next_file_extension}'
        shutil.copy(next_file, backup_file)

    return


def _populate_kana():
    # There are two kana tables in the database to populate: kana and kana_notes. The data comes from
    # the associated spreadsheet which contains two sheets. The first sheet contains all the kana grouped
    # by category. Each category is a table on the first sheet. The second sheet contains a single table
    # that holds notes for all the kana in the "Basic" group.
    #
    # To populate the kana database tables..
    #   1. read the kana data from the associated spreadsheet and prepare it for insertion into the database
    #   2. insert the kana data from the first sheet into the kana table in the database
    #   3. get the row_ids from the new kana table in the database all the "Basic" category kana
    #   4. insert the "Basic" kana notes into the kana_notes table in the database (using the row_ids fetched
    #      in step 3

    workbook = _KanaWorkbook()

    # Populate the database's "kana" table
    rows: list[_dbms.Row] = []
    for kana in workbook.kana.values():
        rows.append(_dbms.Row([kana.romaji, kana.hiragana, kana.katakana, kana.category] + _quiz_metric_values))
    _dbms.insert_many(table_name='kana', column_definitions=_TABLE_SCHEMAS['kana'], rows=rows)

    # Get the row_ids of the "Basic" kana items and create a dict to map those items to row ids
    col_defs = _dbms.ColumnDefinitions({'hiragana': _dbms.ColumnTypes.TEXT, 'katakana': _dbms.ColumnTypes.TEXT})
    rows_from_db = _dbms.fetch_where(table_name='kana', column_definitions=col_defs,
                                     where_clause='category = "Basic" and romaji != "n/m"')

    katakana_id_map: dict[str, int] = {}
    hiragana_id_map: dict[str, int] = {}
    for row in rows_from_db:
        hiragana_id_map[row[1]] = row[0]
        katakana_id_map[row[2]] = row[0]

    # Prepare the set of rows to insert into the database's "kana_notes" table
    rows: list[_dbms.Row] = []
    for kana in workbook.kana.values():
        if kana.category == 'Basic' and kana.romaji != 'n/m':
            row_id = hiragana_id_map[kana.hiragana] if kana.hiragana in hiragana_id_map.keys() \
                else katakana_id_map[kana.katakana]
            rows.append(_dbms.Row([row_id, kana.hiragana_note, kana.katakana_note]))

    # Insert the prepared rows into the kana_notes table
    _dbms.insert_many('kana_notes', column_definitions=_TABLE_SCHEMAS['kana_notes'], rows=rows)

    return


def _populate_vocabulary():

    workbook = _VocabWorkbook()
    rows = []
    wb_word_map: dict[str, _VocabWorkbookRecord] = {}  # key is the associated word's kana value

    # Populate the database's "vocab" table first
    for wb_word in workbook.words:
        wb_word_map[wb_word.kana] = wb_word
        rows.append(_dbms.Row([wb_word.english, wb_word.romaji, wb_word.kana, wb_word.kanji, wb_word.part_of_speech] +
                              _quiz_metric_values))

    _dbms.insert_many(table_name='vocab', column_definitions=_TABLE_SCHEMAS['vocab'], rows=rows)

    # Get the row_ids of the records just created; they are needed to populate the remaining vocab tables.
    # Will place them into a dict (word_id_map) whose keys are each word's kana form and whose values are
    # the associated row id
    col_defs = _dbms.ColumnDefinitions({'kana_w': _dbms.ColumnTypes.TEXT})
    rows_from_db = _dbms.fetch_where(table_name='vocab', column_definitions=col_defs,
                                     where_clause='1 = 1')
    db_word_id_map = {r[1]: r[0] for r in rows_from_db}

    # Next, build the row sets for the vocab_notes and vocab_tags tables
    note_rows = []
    tag_rows = []
    for kana, wb_word in wb_word_map.items():
        word_id = db_word_id_map[kana]
        if wb_word.note:
            note_rows.append(_dbms.Row([word_id, wb_word.note]))
        if wb_word.tags:
            tag_rows += [_dbms.Row([word_id, tag]) for tag in wb_word.tags]

    # Populate the vocab_notes and vocab_tags tables
    _dbms.insert_many('vocab_notes', _TABLE_SCHEMAS['vocab_notes'], note_rows)
    _dbms.insert_many('vocab_tags', _TABLE_SCHEMAS['vocab_tags'], tag_rows)

    return


def _delete_word(db_word: _DatabaseWordRecord):

    # First delete any note this word has from the vocab_notes table.
    # We do that by querying for a record in the vocab_notes table whose word_id matches the word_id
    # of the vocab word record we're deleting.
    col_defs = _dbms.ColumnDefinitions({'word_id': _dbms.ColumnTypes.INTEGER})
    rows = _dbms.fetch_where('vocab_notes', col_defs, where_clause=f'word_id = {db_word.word_id}')

    if db_word.note:
        assert len(rows) == 1
        _dbms.delete('vocab_notes', row_id=rows[0][0])
    else:
        assert len(rows) == 0

    # Next delete any tags this word has from the vocab_tags table.
    # Again, we need to rowids of all records in this table whose word_id matches that of the word we're deleting.
    rows = _dbms.fetch_where('vocab_tags', col_defs, where_clause=f'word_id = {db_word.word_id}')
    tag_row_ids: list[int] = [int(row[0]) for row in rows]

    if db_word.tags:
        assert len(rows) == len(db_word.tags)
        for tag_row_id in tag_row_ids:
            _dbms.delete('vocab_tags', tag_row_id)
    else:
        assert len(rows) == 0

    # Finally, we delete the word's record in the vocab table
    _dbms.delete('vocab', db_word.word_id)

    return


def _add_word(wb_word: _VocabWorkbookRecord):

    # First we need to add the vocab table record for this word; we will need the rowid of this new
    # record when we add any note and tag records.
    row = _dbms.Row([wb_word.english, wb_word.romaji, wb_word.kana, wb_word.kanji, wb_word.part_of_speech] +
                    _quiz_metric_values)
    new_word_id = _dbms.insert('vocab', _TABLE_SCHEMAS['vocab'], row)

    if wb_word.note:
        # Add a record to the vocab_notes table for this word
        row = _dbms.Row([new_word_id, wb_word.note])
        _dbms.insert('vocab_notes', _TABLE_SCHEMAS['vocab_notes'], row)

    if wb_word.tags:
        # Add records to the vocab_tags table for each of this word's tags
        for tag in wb_word.tags:
            row = _dbms.Row([new_word_id, tag])
            _dbms.insert('vocab_tags', _TABLE_SCHEMAS['vocab_tags'], row)

    return


def _update_word(db_word: _DatabaseWordRecord, wb_word: _VocabWorkbookRecord):
    assert db_word.kana == wb_word.kana

    # Set up the row to be updated in the vocab table
    # Note we don't have to explicitly deal with this word's quiz metrics beyond making sure they are
    # not referenced in the dbms.ColumnDefinitions parameter passed to dbms.update().
    col_defs = _dbms.ColumnDefinitions({k: v for k, v in _TABLE_SCHEMAS['vocab'].items()
                                        if k not in _QUIZ_METRIC_COLUMNS})
    row = _dbms.Row([wb_word.english, wb_word.romaji, wb_word.kana, wb_word.kanji, wb_word.part_of_speech])
    _dbms.update('vocab', col_defs, row_id=db_word.word_id, row=row)

    if wb_word.note:
        # There is a note for this row in the workbook.
        if db_word.note:
            # There is also a note for this row in the database.  Are they different?
            if wb_word.note != db_word.note:
                # Yes! This word's note is being updated. So we will need to get the rowid of the existing
                # note in the vocab_notes table.
                col_defs = _dbms.ColumnDefinitions({'word_id': _dbms.ColumnTypes.INTEGER})
                rows = _dbms.fetch_where('vocab_notes', column_definitions=col_defs,
                                         where_clause=f'word_id = {db_word.word_id}')
                assert len(rows) == 1
                note_rowid = rows[0][0]
                _dbms.update('vocab_notes', _TABLE_SCHEMAS['vocab_notes'],
                             row_id=note_rowid, row=_dbms.Row([db_word.word_id, wb_word.note]))
        else:
            # The note in wb_word is new for this word in the database; we need to do an insert instead of an
            # update
            row = _dbms.Row([db_word.word_id, wb_word.note])
            _dbms.insert('vocab_notes', _TABLE_SCHEMAS['vocab_notes'], row)

    if wb_word.tags:
        # There are tags for this row in the workbook. Do any need to be updated in the database?
        if db_word.tags:
            # Tags for this word in the database record and not in the workbook record need to be deleted
            # from vocab_tags.
            rows = _dbms.fetch_where('vocab_tags', _TABLE_SCHEMAS['vocab_tags'],
                                     where_clause=f'word_id = {db_word.word_id}')
            tag_to_rowid_map = {str(row[2]): int(row[0]) for row in rows}
            for tag in db_word.tags:
                if tag.value not in wb_word.tags:
                    _dbms.delete('vocab_tags', row_id=tag_to_rowid_map[tag.value])

            # Tags for this word in the workbook record and not in the database record need
            # to be added to the vocab_tags table.
            for tag in wb_word.tags:
                if tag not in [t.value for t in db_word.tags]:
                    _dbms.insert('vocab_tags', _TABLE_SCHEMAS['vocab_tags'], row=_dbms.Row([db_word.word_id, tag]))

        else:
            # There are no existing tags for this word in the database; we can simply insert all the
            # tags contained in the workbook record.
            for tag in wb_word.tags:
                row = _dbms.Row([db_word.word_id, tag])
                _dbms.insert('vocab_tags', _TABLE_SCHEMAS['vocab_tags'], row)

    return


def _update_vocabulary():

    workbook = _VocabWorkbook()
    database = _VocabDatabase()
    num_words_updated = 0
    num_words_added = 0
    num_words_deleted = 0

    print('')

    # Identify records to delete
    # Are there any words that need to be deleted? I.e., are there any words in the database that do not
    # appear in the workbook?
    for db_word in database.words:
        if db_word.kana not in workbook.word_map.keys():
            num_words_deleted += 1
            _delete_word(db_word)

    # Are there any words that need to be added or updated? Answering both of these questions involves
    # visiting every word in the spreadsheet, so we'll answer both questions together.
    db_kana_list = [w.kana for w in database.words]
    for wb_word in workbook.words:

        # Does this spreadsheet word need to be added to the database?
        if wb_word.kana not in db_kana_list:
            num_words_added += 1
            _add_word(wb_word)

        # Does this spreadsheet word need to be updated in the database?
        else:
            db_word = database.word_map[wb_word.kana]
            if not db_word.is_equal(wb_word):
                num_words_updated += 1
                _update_word(db_word, wb_word)

    print(f'>>>>> store._update_vocabulary(): {num_words_added} words added')
    print(f'>>>>> store._update_vocabulary(): {num_words_deleted} words deleted')
    print(f'>>>>> store._update_vocabulary(): {num_words_updated} words updated')

    return


def create_database():

    # TODO: should _backup be moved to the store.dbms/store.spreadsheet level(s)?
    _backup()
    _dbms.create_database()

    return


def create_tables():

    for table_name, column_definitions in _TABLE_SCHEMAS.items():
        _dbms.create_table(table_name, column_definitions)

    return


def populate_tables():

    _backup()
    _populate_kana()
    _populate_vocabulary()

    return


def update_database():

    _backup()
    _update_vocabulary()

    return
