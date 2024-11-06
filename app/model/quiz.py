
from abc import ABC, abstractmethod
import random
from itertools import islice
from random import sample
from typing import Optional
from app.model import Model
from app.utils.exceptions import ResultsNotSet


def _chunk_list(arr_range, arr_size):
    arr_range = iter(arr_range)
    return list(iter(lambda: tuple(islice(arr_range, arr_size)), ()))


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
        return

    @property
    def table(self) -> str:
        assert self._table is not None
        return self._table

    @table.setter
    def table(self, table: str):
        table = table.title()
        assert table in ['Vocabulary', 'Kana']
        self._table = table
        return

    @property
    def type_of_quiz(self) -> str:
        assert self._kind is not None
        return self._kind

    @type_of_quiz.setter
    def type_of_quiz(self, kind: str):
        kind = kind.title()
        all_kinds_of_quizzes = ['Multiple Choice', 'Match', 'Fill In The Blank', 'Jigsaw', 'Match Game']
        vocab_kinds_of_quizzes = ['Multiple Choice', 'Match']
        assert (self._table == 'Vocabulary' and kind in vocab_kinds_of_quizzes) or \
               (self._table == 'Kana' and kind in all_kinds_of_quizzes)
        self._kind = kind
        return

    @property
    def number_of_items(self) -> int:
        return self._number_of_items

    @number_of_items.setter
    def number_of_items(self, cnt: int):
        assert cnt in [5, 10, 15, 20]
        self._number_of_items = cnt
        return

    @property
    def prompt_type(self):
        return self._prompt_type

    @prompt_type.setter
    def prompt_type(self, ptype: str):
        assert (self._table == 'Vocabulary' and ptype in ['English', 'Kana', 'Kanji']) or \
               (self._table == 'Kana' and ptype in ['Romaji', 'Hiragana', 'Kanji'])
        assert (self._prompt_type != self._choice_type) or (self._prompt_type is None and self._choice_type is None)
        self._prompt_type = ptype
        return

    @property
    def choice_type(self):
        return self._choice_type

    @choice_type.setter
    def choice_type(self, ctype: str):
        assert (self._table == 'Vocabulary' and ctype in ['English', 'Kana', 'Kanji']) or \
               (self._table == 'Kana' and ctype in ['Romaji', 'Hiragana', 'Kanji'])
        assert self._prompt_type != self._choice_type
        self._choice_type = ctype
        return

    @property
    def part_of_speech_filter(self) -> list[str]:
        # return self._pos_filter
        raise NotImplementedError('quiz.py/QuizParameters.part_of_speech_filter')

    @part_of_speech_filter.setter
    def part_of_speech_filter(self, pos: list[str]):
        # self._pos_filter = pos
        # return
        raise NotImplementedError('quiz.py/QuizParameters.part_of_speech_filter')

    @property
    def tag_filter(self) -> list[str]:
        # return self._tag_fiter
        raise NotImplementedError('quiz.py/QuizParameters.tag_filter')

    @tag_filter.setter
    def tag_filter(self, tags: list[str]):
        # self._tag_fiter = tags
        # return
        raise NotImplementedError('quiz.py/QuizParameters.tag_filter')

    @property
    def category_filter(self) -> list[str]:
        # return self._category_filter
        raise NotImplementedError('quiz.py/QuizParameters.category_filter')

    @category_filter.setter
    def category_filter(self, categories: list[str]):
        # self._category_filter = categories
        # return
        raise NotImplementedError('quiz.py/QuizParameters.category_filter')


class QuizItem:
    pass


class MultipleChoiceItem(QuizItem):

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


class Quiz(ABC):

    def __init__(self):
        return

    @property
    @abstractmethod
    def items(self) -> list[QuizItem]:
        ...

    @items.setter
    @abstractmethod
    def items(self, itms: list[QuizItem]):
        ...


class MultipleChoiceQuiz(Quiz):

    def __init__(self, params: QuizParameters):

        super().__init__()
        m = Model()

        if params.table == 'Vocabulary':
            prompt_words = sample(m.vocabulary.words, params.number_of_items)
            prompt_word_ids = [w.id for w in prompt_words]
            other_words = [w for w in m.vocabulary.words if w.id not in prompt_word_ids]
            alt_choice_words = sample(other_words, (params.number_of_items * 4))
            alt_choice_words = _chunk_list(alt_choice_words, 4)
        else:
            assert params.table == 'Kana'
            prompt_words = sample(m.alphabet.characters, params.number_of_items)
            prompt_word_ids = [w.id for w in prompt_words]
            other_words = [w for w in m.alphabet.characters if w.id not in prompt_word_ids]
            alt_choice_words = sample(other_words, (params.number_of_items * 4))
            alt_choice_words = _chunk_list(alt_choice_words, 4)

        self._items: list[MultipleChoiceItem] = []
        for i, prompt_word in enumerate(prompt_words):

            if params.prompt_type == 'English':
                prompt = prompt_word.english
            elif params.prompt_type == 'Kana':
                prompt = prompt_word.kana
            elif params.prompt_type == 'Romaji':
                prompt = prompt_word.romaji
            elif params.prompt_type == 'Hiragana':
                prompt = prompt_word.hiragana
            else:  # params.prompt_type == 'Katakana'
                prompt = prompt_word.katakana

            if params.choice_type == 'English':
                answer = prompt_word.english
                choices = [w.english for w in alt_choice_words[i]] + [answer]
                random.shuffle(choices)
            elif params.choice_type == 'Kana':
                answer = prompt_word.kana
                choices = [w.kana for w in alt_choice_words[i]] + [answer]
                random.shuffle(choices)
            elif params.choice_type == 'Romaji':
                answer = prompt_word.romaji
                choices = [w.romaji for w in alt_choice_words[i]] + [answer]
                random.shuffle(choices)
            elif params.choice_type == 'Hiragana':
                answer = prompt_word.hiragana
                choices = [w.hiragana for w in alt_choice_words[i]] + [answer]
                random.shuffle(choices)
            else:  # params.choice_type == 'Katakana'
                answer = prompt_word.katakana
                choices = [w.katakana for w in alt_choice_words[i]] + [answer]
                random.shuffle(choices)

            item = MultipleChoiceItem(prompt, answer, choices)
            self._items.append(item)

        return

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


class MatchQuiz(Quiz):

    def __init__(self, params: QuizParameters):
        super().__init__()
        # return
        raise NotImplementedError('quiz.py/MatchQuiz()')


class FillInTheBlankQuiz(Quiz):

    def __init__(self, params: QuizParameters):
        super().__init__()
        # return
        raise NotImplementedError('quiz.py/FillInTheQuiz()')


class JigsawQuiz(Quiz):

    def __init__(self, params: QuizParameters):
        super().__init__()
        # return
        raise NotImplementedError('quiz.py/JigsawQuiz()')


class MemoryQuiz(Quiz):

    def __init__(self, params: QuizParameters):
        super().__init__()
        # return
        raise NotImplementedError('quiz.py/MemoryQuiz()')


def create_quiz(params: QuizParameters) -> Quiz:

    m = Model()

    quiz_type_map = {
        'Multiple Choice': MultipleChoiceQuiz,
        'Match': MatchQuiz,
        'Fill In The Blank': FillInTheBlankQuiz,
        'Jigsaw': JigsawQuiz,
        'Memory': MemoryQuiz,
    }

    quiz_cls = quiz_type_map[params.type_of_quiz]
    quiz_inst = quiz_cls(params)
    return quiz_inst
