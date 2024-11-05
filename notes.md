
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

## Git commands

- clone from github
  - git clone https://github.com/olli-shamlin/flosetta.git
- push to github
  - git push -u origin main