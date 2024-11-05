
from app.model.vocabulary import Vocabulary
from app.model.alphabet import Alphabet
from typing import Optional


class Model:

    # TODO REFACTOR
    # Change _vocabulary and _alphabet from instance properties to class properties so that
    # the database tables are only loaded once per app session instead of everytime a Model instance is created.

    def __init__(self):
        self._vocabulary: Optional[list[Vocabulary]] = None
        self._alphabet: Optional[Alphabet] = None
        return

    @property
    def vocabulary(self) -> Vocabulary:
        if self._vocabulary is None:
            self._vocabulary = Vocabulary()
        return self._vocabulary

    @property
    def alphabet(self) -> Alphabet:
        if self._alphabet is None:
            self._alphabet = Alphabet()
        return self._alphabet

    @property
    def is_dirty(self) -> bool:
        return self.alphabet.is_dirty or self.vocabulary.is_dirty

    def save(self) -> None:

        if self.alphabet.is_dirty:
            self.alphabet.save()
        if self.vocabulary.is_dirty:
            self.vocabulary.save()

        return
