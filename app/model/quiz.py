
from typing import Optional
from app.utils.exceptions import ResultsNotSet


class QuizParameters:

    def __init__(self):
        self._table: Optional[str] = None
        self._kind: Optional[str] = None
        self._number_of_items: Optional[int] = None
        self._prompt_type: Optional[str] = None
        self._choice_type: Optional[str] = None
        self._pos_filter: Optional[list[str]] = None
        self._tag_fiter: Optional[list[str]] = None
        self._category_filter: Optional[list[str]] = None

    @property
    def table(self) -> str:
        assert self._table is not None
        return self._table

    @table.setter
    def table(self, table: str):
        table = table.title()
        assert table in ['Vocabulary', 'Kana']
        self._table = table

    @property
    def kind(self) -> str:
        assert self._kind is not None
        return self._kind

    @kind.setter
    def kind(self, kind: str):
        kind = kind.title()
        all_kinds_of_quizzes = ['Multiple Choice', 'Match', 'Fill In The Blank', 'Jigsaw', 'Match Game']
        vocab_kinds_of_quizzes = ['Multiple Choice', 'Match']
        assert (self._table == 'Vocab' and kind in vocab_kinds_of_quizzes) or \
               (self._table == 'Kana' and kind in all_kinds_of_quizzes)
        self._kind = kind


class QuizItem:

    pass


class MultipleChoiceItem:

    def __init__(self, prompt: str, answer: str, choices: list[str]):
        self._prompt: str = prompt
        self._answer: str = answer
        self._choices: list[str] = choices
        self._response: Optional[str] = None

    @property
    def prompt(self) -> str:
        return self._prompt

    @property
    def answer(self) -> str:
        return self._answer

    @property
    def choices(self) -> list[str]:
        return self._choices

    @property
    def response(self) -> str:
        assert self._response is not None
        return self._response

    @response.setter
    def response(self, r: str):
        assert self._response is None
        self._response = r
        return

    @property
    def answered_correct(self) -> bool:
        assert self._response is not None
        return self._answer == self._response


class Quiz:

    def __init__(self):
        return


class MultipleChoiceQuiz(Quiz):

    def __init__(self, num_items: int):

        super().__init__()
        abcde = 'ABCDE'

        self._items: list[MultipleChoiceItem] = []
        self._results: Optional[list[str]] = None

        for i in range(num_items):
            prompt = f'PROMPT-{i + 1}'
            choices = [f'CHOICE-{i + 1}{k}' for k in abcde]
            answer = choices[i % len(abcde)]
            self._items.append(MultipleChoiceItem(prompt, answer, choices))

    @property
    def items(self) -> list[MultipleChoiceItem]:
        return self._items

    def add_results(self, results: list[str]):
        assert self._results is None
        assert len(results) == len(self._items)
        for i, item in enumerate(self._items):
            item.response = results[i]
        return

    @property
    def correct(self) -> int:
        assert all([i.response is not None for i in self._items])
        return len([i for i in self._items if i.answered_correct])

    @property
    def incorrect(self) -> int:
        assert all([i.response is not None for i in self._items])
        return len([i for i in self._items if not i.answered_correct])


class Match(Quiz):

    pass


class FillInTheBlank(Quiz):

    pass


class Jigsaw(Quiz):

    pass


class Memory(Quiz):

    pass
