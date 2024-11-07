
from app.model.statistic import Statistic
from app.model.dbms import fetch_kana, update_row, fetch_kana_categories
from app.utils import debug_msg
from collections import UserList
from typing import Optional


class Character:

    def __init__(self, kana_id: int, english: str, hiragana: str, katakana: str, category: str,
                 hiragana_mnemonic: Optional[str], katakana_mnemonic: Optional[str],
                 stat_quizzed: int, stat_correct: int, stat_consecutive_correct: int, stat_consecutive_wrong: int):
        self._id: int = kana_id
        self._category: str = category
        self._english: str = english
        self._hiragana: str = hiragana
        self._hiragana_mnemonic: Optional[str] = hiragana_mnemonic
        self._katakana: str = katakana
        self._katakana_mnemonic: Optional[str] = katakana_mnemonic
        self._stats: Statistic = Statistic(stat_quizzed, stat_correct, stat_consecutive_correct, stat_consecutive_wrong)

        return

    @property
    def id(self) -> int:
        return self._id

    @property
    def category(self) -> str:
        return self._category

    @property
    def romaji(self) -> str:
        return self._english

    @property
    def hiragana(self) -> str:
        return self._hiragana

    @property
    def hiragana_mnemonic(self) -> Optional[str]:
        return self._hiragana_mnemonic

    @property
    def katakana(self) -> str:
        return self._katakana

    @property
    def katakana_mnemonic(self) -> Optional[str]:
        return self._katakana_mnemonic

    @property
    def statistics(self) -> Statistic:
        return self._stats

    @property
    def is_dirty(self) -> bool:
        return self._stats.is_dirty

    def update(self) -> None:
        cols = {
            'quizzed': self.statistics.quizzed,
            'correct': self.statistics.correct,
            'consecutive_correct': self.statistics.consecutive_correct,
            'consecutive_wrong': self.statistics.consecutive_incorrect
        }
        update_row('kana', self.id, cols)
        self.statistics.synced()
        return


class Syllabary(UserList):

    _characters: Optional[list[Character]] = None

    def __init__(self):

        if Syllabary._characters is None:

            rows = fetch_kana()
            Syllabary._characters = []

            for row in rows:
                character = Character(kana_id=row[0], category=row[6], english=row[1],
                                      hiragana=row[2], hiragana_mnemonic=row[3],
                                      katakana=row[4],katakana_mnemonic=row[5],
                                      stat_quizzed=row[7], stat_correct=row[8],
                                      stat_consecutive_correct=row[9], stat_consecutive_wrong=row[10])
                Syllabary._characters.append(character)

        super().__init__(Syllabary._characters)
        return

    @property
    def categories(self) -> list[str]:
        raise NotImplementedError('alphabet.py/Syllabary.categories')

    @property
    def is_dirty(self) -> bool:
        return any([c.is_dirty for c in self.data])

    def save(self) -> None:
        n = 0
        debug_msg('saving alphabet')

        for character in self.data:
            if character.is_dirty:
                character.update()
                n += 1

        debug_msg(f'done saving alphabet; {n} characters updated')
        return
