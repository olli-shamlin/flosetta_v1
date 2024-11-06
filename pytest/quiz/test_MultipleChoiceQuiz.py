
from app.model.quiz import create_quiz, QuizParameters


def test_mcq_vocab():

    params = QuizParameters()
    params.table = 'Vocabulary'
    params.number_of_items = 5
    params.type_of_quiz = 'Multiple Choice'
    params.prompt_type = 'English'
    params.choice_type = 'Kana'

    quiz = create_quiz(params)

    assert len(quiz.items) == params.number_of_items

    return


def test_mcq_kana():

    params = QuizParameters()
    params.table = 'Kana'
    params.number_of_items = 5
    params.type_of_quiz = 'Multiple Choice'
    params.prompt_type = 'Romaji'
    params.choice_type = 'Hiragana'

    quiz = create_quiz(params)

    assert len(quiz.items) == params.number_of_items

    return
