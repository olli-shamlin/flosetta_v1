
from flask import render_template, redirect, request
from app import app
from app.utils import resolve_icon, debug_msg
from app.utils.kana_reference import kana_reference_tables
from app.model import Model
from app.model.quiz import create_quiz, MultipleChoiceQuiz
from app.model.quiz import QuizParameters
from app.forms import MultipleChoiceQuizForm
from app.forms import QuizSetupForm1, QuizSetupForm2a, QuizSetupForm2b, QuizSetupForm3
from app.forms import QuizSetupForm4, QuizSetupForm5, QuizSetupForm6


class _PassTheBaton:

    _object = None

    @property
    def object(self):
        assert _PassTheBaton._object is not None
        o = _PassTheBaton._object
        _PassTheBaton._object = None
        return o

    @object.setter
    def object(self, obj):
        assert _PassTheBaton._object is None
        _PassTheBaton._object = obj
        return

    def drop(self) -> None:
        _PassTheBaton._object = None


_BATON = _PassTheBaton()


@app.route('/')
@app.route('/index')
@app.route('/vocab')
def index():
    return render_template('vocabulary.html',
                           words=Model().vocabulary.words,
                           title='Vocabulary',
                           emoji=resolve_icon('backpack'))


@app.route('/kana')
def kana():
    return render_template('kana.html', reftabs=kana_reference_tables(), title='Kana', emoji=resolve_icon('brilliance'))


@app.route('/statistics')
def statistics():
    return render_template('statistics.html', title='Statistics', emoji=resolve_icon('speedometer2'))


# @app.route('/quiz_setup', methods=['GET', 'POST'])
# def quiz_setup():
#     form = QuizSetupForm()
#     if form.validate_on_submit():
#         debug_msg(f'datasource={form.datasource.data}')
#         debug_msg(f'type={form.type.data}')
#         debug_msg(f'num_prompts={form.num_prompts.data}')
#         debug_msg(f'vocab_prompt_type={form.vocab_prompt_type.data}')
#         debug_msg(f'kana_prompt_type={form.kana_prompt_type.data}')
#         debug_msg(f'vocab_response_type={form.vocab_response_type.data}')
#         debug_msg(f'kana_response_type={form.kana_response_type.data}')
#         debug_msg(f'vocab_pos_filter={form.vocab_pos_filter.data}')
#         debug_msg(f'vocab_tag_filter={form.vocab_tag_filter.data}')
#         debug_msg(f'kana_filter={form.kana_filter.data}')
#         return redirect('/quiz_setup')
#     # Replace the "placeholder" choices (set in the code that defines the form) with sets of choices from the
#     # model/dbms.
#     form.vocab_pos_filter.choices = Model().vocabulary.parts_of_speech
#     form.vocab_tag_filter.choices = Model().vocabulary.tags
#     form.kana_filter.choices = Model().alphabet.categories
#     context = RendererContext()
#     return render_template('quiz_setup.html', form=form, renderer_context=context, title='Quiz Setup',
#                            emoji=resolve_icon('question'))

@app.route('/quiz_setup', methods=['GET', 'POST'])
def quiz_setup():
    form = QuizSetupForm1()
    if form.validate_on_submit():
        params = QuizParameters()
        params.table = form.table.data
        debug_msg(f'QuizSetUpForm1: table selected = {params.table}')
        _BATON.object = params
        return redirect('/quiz_setup2')
    return render_template('quiz_setup.html', form=form, title='Quiz Setup', emoji=resolve_icon('question'))


@app.route('/quiz_setup2', methods=['GET', 'POST'])
def quiz_setup2():
    params = _BATON.object
    form = QuizSetupForm2a() if params.table == 'Vocabulary' else QuizSetupForm2b()
    if form.validate_on_submit():
        params.type_of_quiz = form.quiz_type.data
        debug_msg(f'QuizSetupForm2[a|b]: quiz type selected = {params.type_of_quiz}')
        _BATON.object = params
        return redirect('/quiz_setup3')
    _BATON.object = params
    return render_template('quiz_setup.html', form=form, title='Quiz Setup', emoji=resolve_icon('question'))


@app.route('/quiz_setup3', methods=['GET', 'POST'])
def quiz_setup3():
    params = _BATON.object
    form = QuizSetupForm3()
    if form.validate_on_submit():
        params.number_of_items = int(form.number_of_items.data)
        debug_msg(f'QuizSetupForm3: number of items selected = {params.number_of_items}')
        _BATON.object = params
        return redirect('/quiz_setup4')
    _BATON.object = params
    return render_template('quiz_setup.html', form=form, title='Quiz Setup', emoji=resolve_icon('question'))


@app.route('/quiz_setup4', methods=['GET', 'POST'])
def quiz_setup4():
    params = _BATON.object
    form = QuizSetupForm4()
    if form.is_submitted():  # form.validate_on_submit() doesn't come back True when the submit button is clicked
        params.prompt_type = form.prompt_type.data
        debug_msg(f'QuizSetupForm4: prompt type selected = {params.prompt_type}')
        _BATON.object = params
        return redirect('/quiz_setup5')
    choices = ['English', 'Kana', 'Kanji'] if params.table == 'Vocabulary' else ['Romaji', 'Hiragana', 'Katakana']
    form.prompt_type.choices = choices
    _BATON.object = params
    return render_template('quiz_setup.html', form=form, title='Quiz Setup', emoji=resolve_icon('question'))


@app.route('/quiz_setup5', methods=['GET', 'POST'])
def quiz_setup5():
    params = _BATON.object
    form = QuizSetupForm5()
    if form.is_submitted():  # form.validate_on_submit() doesn't come back True when the submit button is clicked
        params.choice_type = form.choice_type.data
        debug_msg(f'QuizSetupForm5: choice type selected = {params.choice_type}')
        _BATON.object = params
        return redirect('/quiz_setup6')

    # Create the list of possible choice types
    # The user should be presented with the set of "word" forms *except* the "word" form chosen for quiz item prompts
    choices = ['English', 'Kana', 'Kanji'] if params.table == 'Vocabulary' else ['Romaji', 'Hiragana', 'Katakana']
    form.choice_type.choices = [c for c in choices if c != params.prompt_type]

    _BATON.object = params
    return render_template('quiz_setup.html', form=form, title='Quiz Setup', emoji=resolve_icon('question'))


@app.route('/quiz_setup6', methods=['GET', 'POST'])
def quiz_setup6():
    params = _BATON.object
    form = QuizSetupForm6(request.form)
    if request.method == 'POST':
        if form.cancel.data:
            _BATON.drop()
            return redirect('/index')
        elif form.is_submitted():
            _BATON.object = params
            return redirect('/multiple_choice_quiz')
    _BATON.object = params
    return render_template('quiz_start.html', form=form, quiz_params=params,
                           title='Quiz Setup', emoji=resolve_icon('question'))


@app.route('/multiple_choice_quiz', methods=['GET', 'POST'])
def multiple_choice_quiz():
    form = MultipleChoiceQuizForm()
    if form.validate_on_submit():
        quiz = _BATON.object
        quiz.add_results(str(form.responses.data).split('|'))
        _BATON.object = quiz
        return redirect('/quiz_results')
    params = _BATON.object
    quiz = create_quiz(params)
    _BATON.object = quiz
    return render_template('quiz_multiple_choice.html', quiz=quiz, form=form,
                           title='Multiple Choice Quiz', emoji=resolve_icon('question'))


@app.route('/quiz_results')
def quiz_results():
    return render_template('quiz_results.html', quiz=_BATON.object,
                           title='Quiz Results', emoji=resolve_icon('question'))


@app.route('/proto', methods=['GET', 'POST'])
def proto():
    return render_template('proto_quiz_setup_2.html',
                           title='Quiz Options', emoji=resolve_icon('question'))
