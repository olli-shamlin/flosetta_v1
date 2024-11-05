
from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms import SelectMultipleField
from wtforms import RadioField
from wtforms import HiddenField
from wtforms import StringField
from wtforms.widgets import HiddenInput

_PLACE_HOLDER = ['this', 'is', 'a', 'placeholder']


class _Choices:
    datasource = ['Vocabulary', 'Kana']
    type = ['Multiple Choice', 'Match', 'Fill in the Blank', 'Jigsaw']
    num_prompts = ['5', '10', '15', '20']
    vocab_prompt_type = ['English', 'Kana', 'Kanji']
    kana_prompt_type = ['Romaji', 'Hiragana', 'Katakana']
    vocab_response_type = ['English', 'Kana', 'Kanji']
    kana_response_type = ['Romaji', 'Hiragana', 'Katakana']

    # The form elements/controls for the following items are dynamically generated from the database.
    # If we populate these controls' list of choices from the database in the QuizSetupForm below, then the database
    # will be queried *before* the app is running and that prevents me from including code that creates/updates
    # the database that I can run inside this project's venv.

    vocab_pos_filters = _PLACE_HOLDER
    vocab_tag_filters = _PLACE_HOLDER
    kana_filters = _PLACE_HOLDER


class QuizSetupForm(FlaskForm):
    datasource = RadioField('Which data set do you want to be quizzed on?', choices=_Choices.datasource)
    type = RadioField('What type of quiz would you like?', choices=_Choices.type)
    num_prompts = RadioField('How many prompts do you want in the quiz?', choices=_Choices.num_prompts)
    vocab_prompt_type = RadioField('VOCABULARY: How do you want to be prompted?', choices=_Choices.vocab_prompt_type)
    kana_prompt_type = RadioField('KANA: How do you want to be prompted?', choices=_Choices.kana_prompt_type)
    vocab_response_type = RadioField('VOCAB: What form do you want the choices to be?',
                                     choices=_Choices.vocab_response_type)
    kana_response_type = RadioField('KANA: What form do you want the choices to be?',
                                    choices=_Choices.kana_response_type)
    vocab_pos_filter = SelectMultipleField('VOCAB: Which parts of speech do you want to include?',
                                           choices=_Choices.vocab_pos_filters)
    vocab_tag_filter = SelectMultipleField('VOCAB: Which tags do you want to include?',
                                           choices=_Choices.vocab_tag_filters)
    kana_filter = SelectMultipleField('KANA: Which categories do you want to include?', choices=_Choices.kana_filters)
    submit = SubmitField('Continue')


class MultipleChoiceQuizForm(FlaskForm):
    responses = StringField(id='hidden-response-field', default='initial string field value', widget=HiddenInput())
    submit = SubmitField('DONE')
