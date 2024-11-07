
from app.model.syllabary import Syllabary


def test_alphabet_read():

    syllabary = Syllabary()

    # TODO REFACTOR
    # The following code is also in test_model_read.py; it would be good to extract it into it's own function
    # that can be shared between tests
    assert len(syllabary) == 107

    assert syllabary[0].category == 'Modified YO'
    assert syllabary[0].romaji == 'nyo'
    assert syllabary[0].hiragana == 'にょ'
    assert syllabary[0].katakana == 'ニョ'
    assert syllabary[0].hiragana_mnemonic is None
    assert syllabary[0].katakana_mnemonic is None
    assert syllabary[0].statistics.quizzed == 0
    assert syllabary[0].statistics.correct == 0
    assert syllabary[0].statistics.consecutive_correct == 0
    assert syllabary[0].statistics.consecutive_incorrect == 0

    assert syllabary[13].category == 'Modified YU'
    assert syllabary[13].romaji == 'chu'
    assert syllabary[13].hiragana == 'ちゅ'
    assert syllabary[13].katakana == 'チュ'
    assert syllabary[13].hiragana_mnemonic is None
    assert syllabary[13].katakana_mnemonic is None
    assert syllabary[13].statistics.quizzed == 0
    assert syllabary[13].statistics.correct == 0
    assert syllabary[13].statistics.consecutive_correct == 0
    assert syllabary[13].statistics.consecutive_incorrect == 0

    i = 96
    assert syllabary[i].category == 'Modified YA'
    assert syllabary[i].romaji == 'cha'
    assert syllabary[i].hiragana == 'ちゃ'
    assert syllabary[i].katakana == 'チャ'
    assert syllabary[i].hiragana_mnemonic is None
    assert syllabary[i].katakana_mnemonic is None
    assert syllabary[i].statistics.quizzed == 0
    assert syllabary[i].statistics.correct == 0
    assert syllabary[i].statistics.consecutive_correct == 0
    assert syllabary[i].statistics.consecutive_incorrect == 0

    i = 70
    assert syllabary[i].category == 'Dakuten'
    assert syllabary[i].romaji == 'ga'
    assert syllabary[i].hiragana == 'が'
    assert syllabary[i].katakana == 'ガ'
    assert syllabary[i].hiragana_mnemonic is None
    assert syllabary[i].katakana_mnemonic is None
    assert syllabary[i].statistics.quizzed == 0
    assert syllabary[i].statistics.correct == 0
    assert syllabary[i].statistics.consecutive_correct == 0
    assert syllabary[i].statistics.consecutive_incorrect == 0

    i = 30
    assert syllabary[i].category == 'Basic'
    assert syllabary[i].romaji == 'ki'
    assert syllabary[i].hiragana == 'き'
    assert syllabary[i].katakana == 'キ'
    assert syllabary[i].hiragana_mnemonic == 'The key is to keep thinking. This symbol looks like a key.'
    assert syllabary[i].katakana_mnemonic == 'The key is to keep thinking. This looks like a key.'
    assert syllabary[i].statistics.quizzed == 0
    assert syllabary[i].statistics.correct == 0
    assert syllabary[i].statistics.consecutive_correct == 0
    assert syllabary[i].statistics.consecutive_incorrect == 0

    return
