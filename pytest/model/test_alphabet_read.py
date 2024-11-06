
from app.model.alphabet import Alphabet


def test_alphabet_read():

    alphabet = Alphabet()
    characters = alphabet.characters

    # TODO REFACTOR
    # The following code is also in test_model_read.py; it would be good to extract it into it's own function
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

    i = 96
    assert characters[i].category == 'Modified YA'
    assert characters[i].romaji == 'cha'
    assert characters[i].hiragana == 'ちゃ'
    assert characters[i].katakana == 'チャ'
    assert characters[i].hiragana_mnemonic is None
    assert characters[i].katakana_mnemonic is None
    assert characters[i].statistics.quizzed == 0
    assert characters[i].statistics.correct == 0
    assert characters[i].statistics.consecutive_correct == 0
    assert characters[i].statistics.consecutive_incorrect == 0

    i = 70
    assert characters[i].category == 'Dakuten'
    assert characters[i].romaji == 'ga'
    assert characters[i].hiragana == 'が'
    assert characters[i].katakana == 'ガ'
    assert characters[i].hiragana_mnemonic is None
    assert characters[i].katakana_mnemonic is None
    assert characters[i].statistics.quizzed == 0
    assert characters[i].statistics.correct == 0
    assert characters[i].statistics.consecutive_correct == 0
    assert characters[i].statistics.consecutive_incorrect == 0

    i = 30
    assert characters[i].category == 'Basic'
    assert characters[i].romaji == 'ki'
    assert characters[i].hiragana == 'き'
    assert characters[i].katakana == 'キ'
    assert characters[i].hiragana_mnemonic == 'The key is to keep thinking. This symbol looks like a key.'
    assert characters[i].katakana_mnemonic == 'The key is to keep thinking. This looks like a key.'
    assert characters[i].statistics.quizzed == 0
    assert characters[i].statistics.correct == 0
    assert characters[i].statistics.consecutive_correct == 0
    assert characters[i].statistics.consecutive_incorrect == 0

    return
