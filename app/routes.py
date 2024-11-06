
from flask import render_template, redirect, url_for
from wtforms_bootstrap5 import RendererContext
from app import app
from app.utils import resolve_icon, debug_msg
from app.utils.kana_reference import kana_reference_tables
from app.model import Model
from app.model.quiz import Quiz, MultipleChoiceQuiz
from app.forms import QuizSetupForm, MultipleChoiceQuizForm
from typing import Optional


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


@app.route('/quiz_setup', methods=['GET', 'POST'])
def quiz_setup():
    form = QuizSetupForm()
    if form.validate_on_submit():
        debug_msg(f'datasource={form.datasource.data}')
        debug_msg(f'type={form.type.data}')
        debug_msg(f'num_prompts={form.num_prompts.data}')
        debug_msg(f'vocab_prompt_type={form.vocab_prompt_type.data}')
        debug_msg(f'kana_prompt_type={form.kana_prompt_type.data}')
        debug_msg(f'vocab_response_type={form.vocab_response_type.data}')
        debug_msg(f'kana_response_type={form.kana_response_type.data}')
        debug_msg(f'vocab_pos_filter={form.vocab_pos_filter.data}')
        debug_msg(f'vocab_tag_filter={form.vocab_tag_filter.data}')
        debug_msg(f'kana_filter={form.kana_filter.data}')
        return redirect('/quiz_setup')
    # Replace the "placeholder" choices (set in the code that defines the form) with sets of choices from the
    # model/dbms.
    form.vocab_pos_filter.choices = Model().vocabulary.parts_of_speech
    form.vocab_tag_filter.choices = Model().vocabulary.tags
    form.kana_filter.choices = Model().alphabet.categories
    context = RendererContext()
    return render_template('quiz_setup.html', form=form, renderer_context=context, title='Quiz Setup',
                           emoji=resolve_icon('question'))


@app.route('/multiple_choice_quiz', methods=['GET', 'POST'])
def multiple_choice_quiz():
    quiz = MultipleChoiceQuiz(5)
    form = MultipleChoiceQuizForm()
    if form.validate_on_submit():
        quiz.add_results(str(form.responses.data).split('|'))
        _BATON.object = quiz
        return redirect('/quiz_results')
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
