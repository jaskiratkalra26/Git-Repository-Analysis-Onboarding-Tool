from abc import ABC, abstractmethod

class Rule(ABC):
    id = "BASE_RULE"
    severity = "warning"

    def get_lines(self, code: str):
        return [
            (i + 1, line, line.strip())
            for i, line in enumerate(code.splitlines())
        ]

    @abstractmethod
    def evaluate(self, code: str):
        pass
