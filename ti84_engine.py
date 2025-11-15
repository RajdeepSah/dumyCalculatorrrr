"""Core computation engine for the TI-84 style calculator."""
from __future__ import annotations

from dataclasses import dataclass, field
import math
import re
from typing import Callable, Dict, List, Tuple


class TI84Error(Exception):
    """Custom exception raised when the calculator encounters an error."""


@dataclass
class EvaluationResult:
    """Container describing the outcome of an expression evaluation."""

    expression: str
    value: str


@dataclass
class TI84Engine:
    """Compute expressions and manage calculator state such as memory and history."""

    history_limit: int = 20
    memory: float = 0.0
    history: List[EvaluationResult] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Initialise cached maps for evaluation."""
        self._functions: Dict[str, Callable[..., float]] = {
            name: getattr(math, name)
            for name in (
                "sin",
                "cos",
                "tan",
                "asin",
                "acos",
                "atan",
                "log10",
                "sqrt",
                "factorial",
                "fabs",
                "exp",
            )
        }
        # Additional math helpers not part of math module's globals mapping.
        self._functions.update(
            {
                "ln": math.log,
                "log": math.log10,
                "abs": abs,
                "pow": pow,
            }
        )
        self._constants: Dict[str, float] = {
            "pi": math.pi,
            "π": math.pi,
            "e": math.e,
        }

    def clear_memory(self) -> None:
        """Clear the stored memory value."""
        self.memory = 0.0

    def add_to_memory(self, value: float) -> None:
        """Add a number to the stored memory value."""
        self.memory += value

    def subtract_from_memory(self, value: float) -> None:
        """Subtract a number from the stored memory value."""
        self.memory -= value

    def recall_memory(self) -> float:
        """Return the current memory value."""
        return self.memory

    def evaluate(self, expression: str) -> EvaluationResult:
        """Evaluate an expression and record it in history."""
        cleaned = self.prepare_expression(expression)
        try:
            result = self._safe_eval(cleaned)
        except ZeroDivisionError as exc:
            raise TI84Error("ERROR: DIVIDE BY 0") from exc
        except ValueError as exc:
            raise TI84Error("ERROR: MATH") from exc
        except OverflowError as exc:
            raise TI84Error("ERROR: OVERFLOW") from exc
        except Exception as exc:  # pragma: no cover - catch-all for syntax issues
            raise TI84Error("ERROR: SYNTAX") from exc

        result_str = self._format_result(result)
        self._append_history(expression, result_str)
        return EvaluationResult(expression=expression, value=result_str)

    def _append_history(self, expression: str, value: str) -> None:
        """Add an entry to the history while ensuring the limit is honoured."""
        self.history.append(EvaluationResult(expression, value))
        if len(self.history) > self.history_limit:
            self.history = self.history[-self.history_limit :]

    def prepare_expression(self, expression: str) -> str:
        """Translate calculator-friendly syntax into Python expressions."""
        expr = expression.strip()
        if not expr:
            raise TI84Error("ERROR: SYNTAX")

        replacements: List[Tuple[str, str]] = [
            ("Ans", self.history[-1].value if self.history else "0"),
            ("^", "**"),
            ("×", "*"),
            ("÷", "/"),
            ("√", "sqrt"),
        ]
        for old, new in replacements:
            expr = expr.replace(old, new)

        # Replace factorial notation "n!" with factorial(n).
        expr = re.sub(
            r"(?P<target>(?:\([^()]*\)|\b[a-zA-Z_]\w*\b|\d+(?:\.\d+)?))!",
            lambda m: f"math.factorial(int({m.group('target')}))",
            expr,
        )

        return expr

    def evaluate_function(self, expression: str, *, x_value: float) -> float:
        """Evaluate an expression for graphing with a supplied ``x`` value."""
        cleaned = self.prepare_expression(expression)
        return self._safe_eval(cleaned, extra_context={"x": x_value})

    def _safe_eval(self, expression: str, *, extra_context: Dict[str, float] | None = None) -> float:
        """Safely evaluate the expression using a restricted namespace."""
        allowed_names: Dict[str, object] = {
            **self._functions,
            **self._constants,
            "math": math,
            "M": self.memory,
        }
        if extra_context:
            allowed_names.update(extra_context)

        try:
            result = eval(expression, {"__builtins__": {}}, allowed_names)
        except NameError as exc:
            raise TI84Error("ERROR: SYNTAX") from exc
        return float(result)

    @staticmethod
    def _format_result(value: float) -> str:
        """Format numeric results to resemble TI-84 output."""
        if abs(value) < 1e-10:
            value = 0.0
        if abs(value) < 1e4 and value == int(value):
            return str(int(value))
        return f"{value:.10g}"


__all__ = ["TI84Engine", "TI84Error", "EvaluationResult"]
