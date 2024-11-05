
from app.model import Model


def test_model_vocabulary_read(expected_vocab_rows):

    words = Model().vocabulary.words

    # TODO REFACTOR
    # The following code is also in test_vocabulary_read.py; it would be good to extract it into it's own function
    # that can be shared between tests
    assert len(words) == 10

    for i, word in enumerate(words):
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


def test_model_alphabet_read():

    characters = Model().alphabet.characters

    # TODO REFACTOR
    # The following code is also in test_alphabet_read.py; it would be good to extract it into it's own function
    # that can be shared between tests
    assert len(characters) == 107

    assert characters[0].category == 'Modified YO'
    assert characters[0].romaji == 'nyo'
    assert characters[0].hiragana == 'にょ'
    assert characters[0].katakana == 'ニョ'
    assert characters[0].hiragana_mnemonic is None
    assert characters[0].katakana_mnemonic is None
    assert characters[0].statistics.quizzed == 0
    assert characters[0].statistics.correct == 0
    assert characters[0].statistics.consecutive_correct == 0
    assert characters[0].statistics.consecutive_incorrect == 0

    assert characters[13].category == 'Modified YU'
    assert characters[13].romaji == 'chu'
    assert characters[13].hiragana == 'ちゅ'
    assert characters[13].katakana == 'チュ'
    assert characters[13].hiragana_mnemonic is None
    assert characters[13].katakana_mnemonic is None
    assert characters[13].statistics.quizzed == 0
    assert characters[13].statistics.correct == 0
    assert characters[13].statistics.consecutive_correct == 0
    assert characters[13].statistics.consecutive_incorrect == 0

    assert characters[25].category == 'Modified YA'
    assert characters[25].romaji == 'cha'
    assert characters[25].hiragana == 'ちゃ'
    assert characters[25].katakana == 'チャ'
    assert characters[25].hiragana_mnemonic is None
    assert characters[25].katakana_mnemonic is None
    assert characters[25].statistics.quizzed == 0
    assert characters[25].statistics.correct == 0
    assert characters[25].statistics.consecutive_correct == 0
    assert characters[25].statistics.consecutive_incorrect == 0

    assert characters[36].category == 'Dakuten'
    assert characters[36].romaji == 'ga'
    assert characters[36].hiragana == 'が'
    assert characters[36].katakana == 'ガ'
    assert characters[36].hiragana_mnemonic is None
    assert characters[36].katakana_mnemonic is None
    assert characters[36].statistics.quizzed == 0
    assert characters[36].statistics.correct == 0
    assert characters[36].statistics.consecutive_correct == 0
    assert characters[36].statistics.consecutive_incorrect == 0

    assert characters[67].category == 'Basic'
    assert characters[67].romaji == 'ki'
    assert characters[67].hiragana == 'き'
    assert characters[67].katakana == 'キ'
    assert characters[67].hiragana_mnemonic == 'The key is to keep thinking. This symbol looks like a key.'
    assert characters[67].katakana_mnemonic == 'The key is to keep thinking. This looks like a key.'
    assert characters[67].statistics.quizzed == 0
    assert characters[67].statistics.correct == 0
    assert characters[67].statistics.consecutive_correct == 0
    assert characters[67].statistics.consecutive_incorrect == 0

    return
