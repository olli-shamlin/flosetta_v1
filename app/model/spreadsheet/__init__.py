
from numbers_parser import Document
from app.utils import FilePaths as paths, debug_msg
from app.utils.exceptions import SpreadsheetIntegrity


def import_vocab() -> list[dict[str, str]]:

    debug_msg('importing vocab spreadsheet')
    debug_msg(f'vocab spreadsheet path: {paths.vocab_spreadsheet.full_path}')

    doc = Document(paths.vocab_spreadsheet.full_path)
    answer: list[dict[str, str]] = list()

    for sheet in doc.sheets:

        table = sheet.tables[0]

        for row in table.iter_rows(min_row=1, values_only=True):
            word = {
                'english': str(row[0]) if str(row[0]) != 'None' else None,
                'romaji': str(row[1]) if str(row[1]) != 'None' else None,
                'kana': str(row[2]) if str(row[2]) != 'None' else None,
                'kanji': str(row[3]) if str(row[3]) != 'None' else None,
                'pos': str(row[4]) if str(row[4]) != 'None' else None,
                'tags': str(row[5]) if str(row[5]) != 'None' else None,
                'note': str(row[6]).replace('"', "'").replace('“', "'") if str(row[6]) != 'None' else None
            }
            answer.append(word)

    debug_msg('done importing vocab spreadsheet')

    _integrity_checks(answer)

    return answer


def import_kana() -> list[dict[str, str]]:

    debug_msg('importing kana spreadsheet')
    debug_msg(f'kana spreadsheet path: {paths.kana_spreadsheet.full_path}')

    doc = Document(paths.kana_spreadsheet.full_path)
    sheets = doc.sheets
    mnemonic_table = sheets[1].tables[0]
    kana_tables = sheets[0].tables

    mnemonics: dict[str, str] = {}
    for row in mnemonic_table.iter_rows(min_row=1, values_only=True):
        assert str(row[0]) not in mnemonics.keys()
        mnemonics[str(row[0])] = str(row[1])

    answer: list[dict[str, str]] = list()
    for next_table in kana_tables:
        for row in next_table.iter_rows(min_row=1, values_only=True):
            hiragana = str(row[1])
            katakana = str(row[2])
            kana = {
                'romaji': str(row[0]),
                'hiragana': hiragana,
                'hiragana_mnemonic': mnemonics[hiragana] if hiragana in mnemonics.keys() else None,
                'katakana': katakana,
                'katakana_mnemonic': mnemonics[katakana] if katakana in mnemonics.keys() else None,
                'category': next_table.name,
            }
            answer.append(kana)

    debug_msg('done importing kana spreadsheet')

    return answer


def _integrity_checks(word_list: list[dict[str, str]]):

    debug_msg('starting vocab integrity checks')
    problems_found = False
    kana_words: list[str] = []

    for w in word_list:

        if w['kana'] is None:
            problems_found = True
            debug_msg(f'INTEGRITY CHECK ERROR: no value in kana field for {w["english"]}')

        if w['pos'] is None:
            problems_found = True
            debug_msg(f'INTEGRITY CHECK ERROR: no value in part of speech field for {w["pos"]}')

        if w['kana'] in kana_words:
            problems_found = True
            debug_msg(f'INTEGRITY CHECK ERROR: duplicate kana value encountered: {w["kana"]}　({w["english"]})')
        else:
            kana_words.append(w['kana'])

    if problems_found:
        raise SpreadsheetIntegrity()

    debug_msg('vocab integrity checks successfully complete')

    return
