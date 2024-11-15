
from .spreadsheet import import_spreadsheet as _import
from ._exceptions import StoreException
from ._data_files import DataFiles as _files
import store.dbms as _dbms
from typing import Optional


class KanaWorkbookRecord:

    def __init__(self, row: list):
        self._row: list = row

    @property
    def romaji(self) -> str: return self._row[0]

    @property
    def hiragana(self) -> str: return self._row[1]

    @property
    def katakana(self) -> str: return self._row[2]

    @property
    def category(self) -> str: return self._row[3]

    @property
    def hiragana_note(self) -> Optional[str]: return self._row[4]

    @property
    def katakana_note(self) -> Optional[str]: return self._row[5]


class KanaWorkbook:

    def __init__(self):

        workbook = _import(_files.kana_spreadsheet)

        if len(workbook.sheets) != 2:
            raise StoreException(f'Kana workbook should only have two sheets; it has {len(workbook.sheets)}')

        notes_sheet = workbook.sheets[1]
        if len(notes_sheet.tables) != 1:
            raise StoreException(f'Kana workbook note sheet should only have one table; '
                                 f'it has {len(notes_sheet.tables)}')

        kana_sheet = workbook.sheets[0]
        if len(kana_sheet.tables) != 5:
            raise StoreException(f'Kana workbook kana sheet should have exactly 5 tables; '
                                 f'it has {len(kana_sheet.tables)}')

        # Put the data from the "notes" table (which is on the workbook's second sheet) into a dict (the
        # "notes_map" variable) whose keys are kana characters and whose values are that kana character's note.
        notes_table = notes_sheet.tables[0]
        notes_map: dict[str, str] = {}  # key is kana; value is note
        for row in notes_table.rows:
            kana = row[0]
            note = row[1]
            if kana in notes_map.keys():
                raise StoreException(f'Kana "{kana}" occurs more than once in spreadsheet notes table')
            notes_map[kana] = note

        self._rows = {}
        for kana_table in kana_sheet.tables:
            category = kana_table.name
            for row in kana_table.rows:
                romaji = row[0]
                hiragana = row[1]
                katakana = row[2]
                hiragana_note = None
                katakana_note = None
                if kana_table.name == 'Basic' and hiragana != 'ん':
                    try:
                        hiragana_note = notes_map[hiragana]
                        katakana_note = notes_map[katakana]
                    except KeyError as e:
                        raise StoreException(f'no note for "{e}" ("{romaji}") found in kana spreadsheet')
                self._rows[romaji] = \
                    KanaWorkbookRecord([romaji, hiragana, katakana, category, hiragana_note, katakana_note])

    @property
    def kana(self) -> dict[str, KanaWorkbookRecord]: return self._rows


class VocabWorkbookRecord:

    def __init__(self, row: list):
        self._row = row

    @property
    def english(self) -> str: return self._row[0]

    @property
    def romaji(self) -> str: return self._row[1]

    @property
    def kana(self) -> str: return self._row[2]

    @property
    def kanji(self) -> str: return self._row[3]

    @property
    def part_of_speech(self) -> str: return self._row[4]

    @property
    def tags(self) -> list[str]:
        raw_tags = self._row[5]
        if raw_tags is None:
            return []
        tags1 = raw_tags.split(';')
        tags2 = [t.strip() for t in tags1]
        return tags2

    @property
    def note(self) -> str: return self._row[6]


class VocabWorkbook:

    def __init__(self):
        workbook = _import(_files.vocab_spreadsheet)
        self._rows = {}
        for sheet in workbook.sheets:
            for table in sheet.tables:
                for row in table.rows:
                    wbword = VocabWorkbookRecord(row)
                    self._rows[wbword.kana] = wbword
        return

    @property
    def words(self) -> list[VocabWorkbookRecord]: return [w for w in self._rows.values()]

    @property
    def word_map(self) -> dict[str, VocabWorkbookRecord]: return self._rows


class VocabDatabaseNoteRecord:

    def __init__(self, row):
        self._row = row
        return

    @property
    def row_id(self) -> int: return self._row[0]

    @property
    def word_id(self) -> int: return self._row[1]

    @property
    def value(self) -> str: return self._row[2]


class VocabDatabaseTagRecord:  # Note: "records" plural

    def __init__(self, row):
        self._row: list = row

    @property
    def row_id(self) -> int: return self._row[0]

    @property
    def word_id(self) -> int: return self._row[1]

    @property
    def value(self) -> str: return self._row[2]


class DatabaseWordRecord:

    def __init__(self, row, note: Optional[VocabDatabaseNoteRecord], tags: Optional[list[VocabDatabaseTagRecord]]):
        self._row: list = row
        self._note: Optional[VocabDatabaseNoteRecord] = note
        self._tags: Optional[list[VocabDatabaseTagRecord]] = tags
        return

    @property
    def word_id(self) -> int: return self._row[0]

    @property
    def english(self) -> str: return self._row[1]

    @property
    def romaji(self) -> str: return self._row[2]

    @property
    def kana(self) -> str: return self._row[3]

    @property
    def kanji(self) -> str: return self._row[4]

    @property
    def part_of_speech(self) -> str: return self._row[5]

    @property
    def note(self) -> Optional[VocabDatabaseNoteRecord]: return self._note

    @property
    def tags(self) -> Optional[list[VocabDatabaseTagRecord]]: return self._tags

    def is_equal(self, wb_word: VocabWorkbookRecord) -> bool:

        assert self.kana == wb_word.kana

        # If any of the following properties are not the same, the database word is not equal to the spreadsheet word.
        if self.english != wb_word.english:
            return False
        if self.romaji != wb_word.romaji:
            return False
        if self.kanji != wb_word.kanji:
            return False
        if self.part_of_speech != wb_word.part_of_speech:
            return False
        if self.note:
            if self.note.value != wb_word.note:
                return False
        else:  # This database word has no note.
            if wb_word.note is not None:
                return False
        if self.tags:
            if set([t.value for t in self.tags]) != set(wb_word.tags):
                return False
        else:  # This database word has no tags.
            if wb_word.tags:
                return False

        return True


class VocabDatabase:

    def __init__(self):
        self._word_rows = {}  # kana: _DatabaseWordRecord

        note_rows = {}  # key is word_id; value is VocabDatabaseNoteRecord
        tag_rows = {}   # key is word_id: value is list[VocabDatabaseTagRecord]

        rows = _dbms.fetch_all('vocab_notes')
        for row in rows:
            db_note = VocabDatabaseNoteRecord(row)
            assert db_note.word_id not in note_rows.keys()
            note_rows[db_note.word_id] = db_note

        rows = _dbms.fetch_all('vocab_tags')
        for row in rows:
            db_tag = VocabDatabaseTagRecord(row)
            if db_tag.word_id not in tag_rows.keys():
                tag_rows[db_tag.word_id] = []
            tag_rows[db_tag.word_id].append(db_tag)

        rows = _dbms.fetch_all('vocab')
        for row in rows:
            word_id = row[0]
            note = note_rows[word_id] if word_id in note_rows.keys() else None
            tag = tag_rows[word_id] if word_id in tag_rows.keys() else None
            db_word = DatabaseWordRecord(row, note, tag)
            assert db_word.kana not in self._word_rows.keys()
            self._word_rows[db_word.kana] = db_word

        return

    @property
    def words(self) -> list[DatabaseWordRecord]: return [w for w in self._word_rows.values()]

    @property
    def word_map(self) -> dict[str, DatabaseWordRecord]: return self._word_rows
