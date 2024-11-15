
from .dbms import ColumnTypes, ColumnDefinitions


_QUIZ_METRICS = {
    'quizzed': ColumnTypes.INTEGER,
    'correct': ColumnTypes.INTEGER,
    'consecutive_correct': ColumnTypes.INTEGER,
    'consecutive_incorrect': ColumnTypes.INTEGER,
}

QUIZ_METRIC_COLUMNS = _QUIZ_METRICS.keys()

TABLE_SCHEMAS = {
    'vocab':
        ColumnDefinitions(
            {
                'english_w': ColumnTypes.TEXT,
                'romaji_w': ColumnTypes.TEXT,
                'kana_w': ColumnTypes.TEXT,
                'kanji_w': ColumnTypes.TEXT,
                'part_of_speech': ColumnTypes.TEXT
            } | _QUIZ_METRICS,
            unique_column='kana_w'
        ),
    'vocab_notes':
        ColumnDefinitions(
            {
                'word_id': ColumnTypes.INTEGER,
                'note': ColumnTypes.TEXT,
            }
        ),
    'vocab_tags':
        ColumnDefinitions(
            {
                'word_id': ColumnTypes.INTEGER,
                'tag': ColumnTypes.TEXT,
            }
        ),
    'kana':
        ColumnDefinitions(
            {
                'romaji': ColumnTypes.TEXT,
                'hiragana': ColumnTypes.TEXT,
                'katakana': ColumnTypes.TEXT,
                'category': ColumnTypes.TEXT
            } | _QUIZ_METRICS,
            unique_column='romaji'
        ),
    'kana_notes':
        ColumnDefinitions(
            {
                'kana_id': ColumnTypes.INTEGER,
                'katakana_note': ColumnTypes.TEXT,
                'hiragana_note': ColumnTypes.TEXT,
            }
        ),
}


