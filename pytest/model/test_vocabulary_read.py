
from app.model.vocabulary import Vocabulary


def test_words_read(expected_vocab_rows):

    vocabulary = Vocabulary()

    # TODO REFACTOR
    # The following code is also in test_model_read.py; it would be good to extract it into it's own function
    # that can be shared between tests
    assert len(vocabulary) == 100

    for i, word in enumerate(vocabulary):
        assert word.english == expected_vocab_rows[i][0]
        assert word.romaji == expected_vocab_rows[i][1]
        assert word.kana == expected_vocab_rows[i][2]
        assert word.kanji == expected_vocab_rows[i][3]
        assert word.part_of_speech == expected_vocab_rows[i][4]
        assert word.note == expected_vocab_rows[i][5]
        if word.tags is None:
            assert expected_vocab_rows[i][6] is None
        else:
            assert '; '.join(word.tags) == expected_vocab_rows[i][6]
        assert word.statistics.quizzed == expected_vocab_rows[i][7]
        assert word.statistics.correct == expected_vocab_rows[i][8]
        assert word.statistics.consecutive_correct == expected_vocab_rows[i][9]
        assert word.statistics.consecutive_incorrect == expected_vocab_rows[i][10]

    return
