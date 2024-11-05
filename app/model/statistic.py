
class Statistic:

    def __init__(self, quizzed: int, correct: int, consecutive_correct: int, consecutive_wrong):
        self._dirty: bool = False
        self._quizzed: int = quizzed
        self._correct: int = correct
        self._consecutive_correct: int = consecutive_correct
        self._consecutive_wrong: int = consecutive_wrong
        return

    @property
    def quizzed(self) -> int:
        return self._quizzed

    @property
    def correct(self) -> int:
        return self._correct

    @property
    def consecutive_correct(self) -> int:
        return self._consecutive_correct

    @property
    def consecutive_incorrect(self) -> int:
        return self._consecutive_wrong

    @property
    def is_dirty(self) -> bool:
        return self._dirty

    def increment(self, correct: bool):
        self._quizzed += 1
        if correct:
            self._correct += 1
            self._consecutive_correct += 1
            self._consecutive_wrong = 0
        else:
            self._consecutive_correct = 0
            self._consecutive_wrong += 1
        self._dirty = True

    def synced(self):
        self._dirty = False
