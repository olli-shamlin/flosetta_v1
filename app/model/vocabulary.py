
from app.model.statistic import Statistic
from app.model.dbms import fetch_vocab, fetch_parts_of_speech, fetch_word_tags, update_row
from collections import UserList
from typing import Optional
from app.utils import debug_msg


class Word:

    def __init__(self, word_id: int, kana: str, english: Optional[str], romaji: Optional[str],
                 kanji: Optional[str], part_of_speech: Optional[str], note: Optional[str], tags: Optional[str],
                 stat_quizzed: int, stat_correct: int, stat_consecutive_correct: int, stat_consecutive_wrong: int):
        self._word_id: int = word_id
        self._english: Optional[str] = english if english != 'None' else None
        self._romaji: Optional[str] = romaji if romaji != 'None' else None
        assert kana != 'None' and kana is not None
        self._kana: Optional[str] = kana
        self._kanji: Optional[str] = kanji if kanji != 'None' else None
        self._note: Optional[str] = note if note != 'None' else None
        self._pos: Optional[str] = part_of_speech if part_of_speech != 'None' else None
        self._tags: Optional[list[str]] = [t.strip() for t in tags.split(';')] if tags else None
        self._statistics: Statistic = Statistic(stat_quizzed, stat_correct,
                                                stat_consecutive_correct, stat_consecutive_wrong)
        return

    @property
    def id(self) -> int:
        return self._word_id

    @property
    def english(self) -> str:
        return self._english

    @property
    def romaji(self) -> str:
        return self._romaji

    @property
    def kana(self) -> str:
        return self._kana

    @property
    def kanji(self) -> str:
        return self._kanji

    @property
    def note(self) -> str:
        return self._note

    @property
    def part_of_speech(self) -> str:
        return self._pos

    @property
    def tags(self) -> list[str]:
        return self._tags

    @property
    def statistics(self) -> Statistic:
        return self._statistics

    @property
    def is_dirty(self) -> bool:
        return self.statistics.is_dirty

    def update(self) -> None:
        cols = {
            'quizzed': self.statistics.quizzed,
            'correct': self.statistics.correct,
            'consecutive_correct': self.statistics.consecutive_correct,
            'consecutive_wrong': self.statistics.consecutive_incorrect
        }
        update_row('vocab', self.id, cols)
        self.statistics.synced()
        return


class Vocabulary(UserList):

    _words: Optional[list[Word]] = None

    def __init__(self):

        if Vocabulary._words is None:

            rows = fetch_vocab()
            Vocabulary._words = []

            for row in rows:
                word = Word(word_id=row[0], english=row[1], romaji=row[2], kana=row[3], kanji=row[4],
                            part_of_speech=row[5], note=row[6],tags=row[7],
                            stat_quizzed=row[8], stat_correct=row[9],
                            stat_consecutive_correct=row[10], stat_consecutive_wrong=row[11])
                Vocabulary._words.append(word)

        super().__init__(Vocabulary._words)
        return

    @property
    def parts_of_speech(self) -> list[str]:
        rows = fetch_parts_of_speech()
        parts_of_speech = [r[0] for r in rows]
        return parts_of_speech

    @property
    def tags(self) -> list[str]:
        rows = fetch_word_tags()
        tags: list[str] = []
        for r in rows:
            for t in str(r[0]).split(';'):
                tags.append(t.strip())
        tags = sorted(list(set(tags)))
        return tags

    @property
    def is_dirty(self) -> bool:
        return any([w.is_dirty for w in self.data])

    def save(self) -> None:

        n = 0
        debug_msg('saving vocabulary')

        for word in self.data:
            if word.is_dirty:
                word.update()
                n += 1

        debug_msg(f'done saving vocabulary; {n} characters updated')

        return
