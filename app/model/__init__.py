
from app.model.vocabulary import Vocabulary
from app.model.alphabet import Syllabary
from typing import Optional


class Model:

    _syllabary: Optional[Syllabary] = None

    def __init__(self):
        self._vocabulary: Optional[list[Vocabulary]] = None
        # self._alphabet: Optional[Alphabet] = None
        return

    @property
    def vocabulary(self) -> Vocabulary:
        if self._vocabulary is None:
            self._vocabulary = Vocabulary()
        return self._vocabulary

    @property
    def syllabary(self) -> Syllabary:
        if Model._syllabary is None:
            Model._syllabary = Syllabary()
        return Model._syllabary

    @property
    def is_dirty(self) -> bool:
        return self.syllabary.is_dirty or self.vocabulary.is_dirty

    def save(self) -> None:

        if self.syllabary.is_dirty:
            self.syllabary.save()
        if self.vocabulary.is_dirty:
            self.vocabulary.save()

        return
