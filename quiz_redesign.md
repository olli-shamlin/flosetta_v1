
# Initial API

## Class QuizItem

### Properties

- prompt: str
- answer: str
- choices: list[str]
- response: str
- answered_correctly: bool

### Methods

None

## Class Quiz

### Properties

- items: list[QuizItems]
- correct: int
- incorrect: int

### Methods

- add_results(results: list[str]) -> None