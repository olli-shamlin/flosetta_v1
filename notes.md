
I am referencing the following Flask tutorial while I'm building this app:

- https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world

To figure out how to implement a Sidebar, I am starting with the following reference:

- https://dev.to/codeply/bootstrap-5-sidebar-examples-38pb

for forms with Bootstrap 5, I should check out the following

- https://pypi.org/project/wtforms-bootstrap5/
- https://github.com/helloflask/bootstrap-flask?tab=readme-ov-file

# Quiz Parameters

- for all quiz types _except_ Kana/jigsaw
  - Pick one: Vocab or Kana
  - Pick one: number of items: 5 | 10 | 15 | 20
  - type: multiple choice | match
    - also "fill in the blank" for vocab

- If quiz is one of the following
  - vocab/multiple choice
  - vocab/match
- Then
  - pick one: prompt is english|japanese
  - pick one:

- Optional choices
  - for vocab quizzes
    - part(s) of speech to include
    - tag(s) to include
  - for kana quizzes
    - category/ies to include

# Strategy for implementing multiple choice quiz page(s)

## Step one: "stub" html page

- entirely html/bootstrap/javascript
- quiz parameters hard coded in the page
  - 5 items
  - each item: prompt-i, [choice-1, choice-2, choice-3, choice-4, choice-5]
  
Flow of control / recipe

- for each quiz item
  - present the prompt
  - present the choices as buttons
  - when user selects a choice
    - turn selected choice button blue
    - disable other choice buttons
    - enable "check" button
    - when "check" button selected
      - populate feedback area with "feedback here"
      - update the status bar
      - change "check" button to "continue" button
      - when "continue" button clicked
        - continue

## Step 2: prototype passing quiz info between browser and app

Nov 4 2024
I managed to sufficiently accomplish step 1 (above) yesterday. Making my
next objective figuring out how to pass a quiz "definition"
from the app to the browser and have the browser return
responses/answers to the quiz. My steps for this objective
are

1. Add stub quiz classes in the app.model package
2. Create a wtform to pass a "quiz definition" to the browser
3. Have the html page add quiz results to some form fields
4. Have the html page post quiz responses back to the
   app when a submit button is clicked

## Nov 5 2024

Got a complete multiple choice quiz flow working with mocked up data.
Decided to move project to github today.  Currently in the process of
setting up the virtual environment of the new project.

### Git commands

- clone from github
  - git clone https://github.com/olli-shamlin/flosetta.git
- push to github
  - git push -u origin main
- commit
  - git commit -m 'comment goes here'
  - UNDO
    - PREFERRED: git revert
    - RISKY: git reset

### Installed python packages

- Flask
- WTForms
- wtforms-bootstrap5 (didn't do it)
- bootstrap-flask (didn't do it)
- flask-boostrap5 (didn't do it)
- flask-bootstrap 
  - didn't work but changed the error!
- uninstalled flask-bootstrap
- uninstalled bootstrap-flask
- boostrap-flask (installed again)
- wtforms-bootstrap5 (installed again)
- numbers-parser
- flask-wtf

...AND WE'RE UP AND RUNNING!

#### Final "pip freeze" output

    blinker==1.8.2
    Bootstrap-Flask==2.4.1
    click==8.1.7
    compact-json==1.8.1
    cramjam==2.9.0
    dominate==2.9.1
    enum-tools==0.12.0
    Flask==3.0.3
    Flask-WTF==1.2.2
    importlib_resources==6.4.5
    itsdangerous==2.2.0
    Jinja2==3.1.4
    MarkupSafe==3.0.2
    numbers-parser==4.14.1
    protobuf==5.28.3
    Pygments==2.18.0
    python-dateutil==2.9.0.post0
    python-snappy==0.7.3
    sigfig==1.3.18
    six==1.16.0
    sortedcontainers==2.4.0
    typing_extensions==4.12.2
    visitor==0.1.3
    wcwidth==0.2.13
    Werkzeug==3.1.2
    WTForms==3.2.1
    wtforms-bootstrap5==0.3.0

## Nov 6 2024

- Got "refreshed" project into github and running locally
- Reasonably working drafts of QuizParamters and 
  MultipleChoiceQuiz written
- Next object is to "wire" those into system to show end-to-end flow from quiz set up pages
  to quiz summary page AND stats saved to dbms
- Today
  - Got quiz flow from setup through results summary working
    for multiple choice quiz with vocab and kana!

### Quiz Setup flow needed for above objective

1. prompt> choose TABLE:
  - vocabulary
  - kana 
2. prompt> choose QUIZ TYPE:
  1. if TABLE is vocabulary
    - multiple choice
    - match
  2. if TABLE is kana
    - multiple choice
    - match
    - jiqsaw
    - memory
  3. if QUIZ TYPE in [multiple choice, match]
    1. prompt> NUMBER OF ITEMS
      - 5
      - 10
      - 15
      - 20
    2. prompt> PROMPT TYPE
      3. if TABLE is vocabulary
        - english
        - kana
        - kanji
      4. if TABLE is kana
        - romaji
        - hiragana
        - katakana
    3. prompt> CHOICE TYPE
      - if TABLE is vocabulary
        - same list as above *except* PROMPT TYPE
      - if TABLE is kana
        - same list as above *except* PROMPT TYPE
  
## Nov 7 2024

- Today I want to focus on cleaning up some issues with the model 
  class:
  - current code is not memoizing correctly
  - current code requires three levels to get to words and characters
    (eg, Model().vocabulary.words and Model().alphabet.characters;
    instead I want Model().vocabulary and Model().alphabet)
- Today I also want to explore using github's issue tracking facilities