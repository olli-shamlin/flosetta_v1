
from app.model.vocabulary import Vocabulary
from app.model.syllabary import Syllabary
from typing import Optional


class Model:

    _vocabulary: Optional[Vocabulary] = None
    _syllabary: Optional[Syllabary] = None

    @property
    def vocabulary(self) -> Vocabulary:
        if Model._vocabulary is None:
            Model._vocabulary = Vocabulary()
        return Model._vocabulary

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
