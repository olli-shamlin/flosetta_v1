from app.model.statistic import Statistic
from app.model.syllabary import Character
from app.model.vocabulary import Word


def test_statistic():

    stat = Statistic(0, 0, 0, 0)

    assert stat.quizzed == 0
    assert stat.correct == 0
    assert stat.consecutive_correct == 0
    assert stat.consecutive_incorrect == 0
    assert stat.is_dirty is False

    stat.increment(correct=True)
    stat.increment(correct=True)
    stat.increment(correct=True)

    assert stat.quizzed == 3
    assert stat.correct == 3
    assert stat.consecutive_correct == 3
    assert stat.consecutive_incorrect == 0
    assert stat.is_dirty is True

    stat.increment(correct=False)
    stat.increment(correct=False)

    assert stat.quizzed == 5
    assert stat.correct == 3
    assert stat.consecutive_correct == 0
    assert stat.consecutive_incorrect == 2
    assert stat.is_dirty is True

    stat.increment(correct=True)
    stat.increment(correct=True)
    stat.increment(correct=True)

    assert stat.quizzed == 8
    assert stat.correct == 6
    assert stat.consecutive_correct == 3
    assert stat.consecutive_incorrect == 0
    assert stat.is_dirty is True

    return


def test_statistics_word():

    item = Word(1, 'kana', 'english', 'romaji', 'kanji', 'pos', 'note', None, 0, 0, 0, 0)

    assert item.statistics.quizzed == 0
    assert item.statistics.correct == 0
    assert item.statistics.consecutive_correct == 0
    assert item.statistics.consecutive_incorrect == 0
    assert item.statistics.is_dirty is False

    item.statistics.increment(correct=True)
    item.statistics.increment(correct=True)
    item.statistics.increment(correct=True)

    assert item.statistics.quizzed == 3
    assert item.statistics.correct == 3
    assert item.statistics.consecutive_correct == 3
    assert item.statistics.consecutive_incorrect == 0
    assert item.statistics.is_dirty is True

    item.statistics.increment(correct=False)
    item.statistics.increment(correct=False)

    assert item.statistics.quizzed == 5
    assert item.statistics.correct == 3
    assert item.statistics.consecutive_correct == 0
    assert item.statistics.consecutive_incorrect == 2
    assert item.statistics.is_dirty is True

    item.statistics.increment(correct=True)
    item.statistics.increment(correct=True)
    item.statistics.increment(correct=True)

    assert item.statistics.quizzed == 8
    assert item.statistics.correct == 6
    assert item.statistics.consecutive_correct == 3
    assert item.statistics.consecutive_incorrect == 0
    assert item.statistics.is_dirty is True

    return


def test_statistics_character():

    item = Character(1, 'english', 'hiragana', 'katakana', 'category', None, None, 0, 0, 0, 0)

    assert item.statistics.quizzed == 0
    assert item.statistics.correct == 0
    assert item.statistics.consecutive_correct == 0
    assert item.statistics.consecutive_incorrect == 0
    assert item.statistics.is_dirty is False

    item.statistics.increment(correct=True)
    item.statistics.increment(correct=True)
    item.statistics.increment(correct=True)

    assert item.statistics.quizzed == 3
    assert item.statistics.correct == 3
    assert item.statistics.consecutive_correct == 3
    assert item.statistics.consecutive_incorrect == 0
    assert item.statistics.is_dirty is True

    item.statistics.increment(correct=False)
    item.statistics.increment(correct=False)

    assert item.statistics.quizzed == 5
    assert item.statistics.correct == 3
    assert item.statistics.consecutive_correct == 0
    assert item.statistics.consecutive_incorrect == 2
    assert item.statistics.is_dirty is True

    item.statistics.increment(correct=True)
    item.statistics.increment(correct=True)
    item.statistics.increment(correct=True)

    assert item.statistics.quizzed == 8
    assert item.statistics.correct == 6
    assert item.statistics.consecutive_correct == 3
    assert item.statistics.consecutive_incorrect == 0
    assert item.statistics.is_dirty is True

    return
