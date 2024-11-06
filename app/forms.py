
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


class QuizSetupForm1(FlaskForm):
    """Choose type of table"""
    table = RadioField('What do you want to be quizzed on?', choices=['Vocabulary', 'Kana'])
    submit = SubmitField('Continue')


class QuizSetupForm2a(FlaskForm):
    """Choose type of quiz for Vocabulary"""
    quiz_type = RadioField('What kind of quiz do you want?', choices=['Multiple Choice', 'Match'])
    submit = SubmitField('Continue')


class QuizSetupForm2b(FlaskForm):
    """Choose type of quiz for Kana"""
    quiz_type = RadioField('What kind of quiz do you want?', choices=['Multiple Choice', 'Match', 'Jigsaw', 'Memory'])
    submit = SubmitField('Continue')


class QuizSetupForm3(FlaskForm):
    """Choose number of items to include in quiz"""
    number_of_items = RadioField('How many items do you want in the quiz?', choices=[5, 10, 15, 20])
    submit = SubmitField('Continue')


class QuizSetupForm4(FlaskForm):
    """Choose word form for PROMPT; this form's prompt_type choices are set by the calling view"""
    prompt_type = RadioField('What word form do you want to be prompted with?', choices=['PLACEHOLDER'])
    submit = SubmitField('Continue')


class QuizSetupForm5(FlaskForm):
    """Choose word form for CHOICES; this form's choice_types choices are set bye the calling view"""
    choice_type = RadioField('What word form do you want to for choices?', choices=['PLACEHOLDER'])
    submit = SubmitField('Continue')


class QuizSetupForm6(FlaskForm):
    """This form is used in conjunction with the quiz setup summary page."""
    cancel = SubmitField('Cancel', render_kw={'formnovalidate': True})
    submit = SubmitField('Start')


class MultipleChoiceQuizForm(FlaskForm):
    responses = StringField(id='hidden-response-field', default='initial string field value', widget=HiddenInput())
    submit = SubmitField('DONE')
