"""Graphing support for the TI-84 style calculator."""
from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Dict, Iterable, List, Tuple

import matplotlib.pyplot as plt

from ti84_engine import TI84Engine, TI84Error


@dataclass
class GraphWindow:
    """Configuration describing the viewport for the plotted graph."""

    xmin: float = -10
    xmax: float = 10
    ymin: float = -10
    ymax: float = 10

    def as_tuple(self) -> Tuple[float, float, float, float]:
        """Return the window boundaries as ``(xmin, xmax, ymin, ymax)``."""
        return self.xmin, self.xmax, self.ymin, self.ymax


@dataclass
class GraphingEngine:
    """Manage the graphing state and prepare matplotlib plots."""

    calculator: TI84Engine
    equations: Dict[str, str] = field(default_factory=dict)
    window: GraphWindow = field(default_factory=GraphWindow)

    def set_equation(self, label: str, expression: str) -> None:
        """Store or clear an equation slot (e.g. ``Y1``)."""
        clean = expression.strip()
        if clean:
            self.equations[label] = clean
        else:
            self.equations.pop(label, None)

    def get_equations(self) -> Dict[str, str]:
        """Return a copy of the currently configured equations."""
        return dict(self.equations)

    def set_window(self, xmin: float, xmax: float, ymin: float, ymax: float) -> None:
        """Update the viewing window used for plots."""
        if xmin >= xmax or ymin >= ymax:
            raise TI84Error("ERROR: WINDOW")
        self.window = GraphWindow(xmin, xmax, ymin, ymax)

    def auto_window(self) -> None:
        """Estimate a window that captures the graph near the origin."""
        self.window = GraphWindow(-10, 10, -10, 10)

    def plot(self) -> plt.Figure:
        """Render the configured equations into a matplotlib figure."""
        if not self.equations:
            raise TI84Error("ERROR: NO FUNCTION")

        figure, axis = plt.subplots()
        axis.grid(True, which="both", linestyle="--", linewidth=0.5)
        axis.axhline(0, color="black", linewidth=0.75)
        axis.axvline(0, color="black", linewidth=0.75)

        xmin, xmax, ymin, ymax = self.window.as_tuple()
        axis.set_xlim(xmin, xmax)
        axis.set_ylim(ymin, ymax)

        xs = self._generate_points(xmin, xmax, count=400)
        for label, expression in sorted(self.equations.items()):
            ys = self._evaluate_series(expression, xs)
            axis.plot(xs, ys, label=label)

        self._annotate_intersections(axis, xs)

        axis.legend()
        axis.set_title("TI-84 Style Graph")
        axis.set_xlabel("X")
        axis.set_ylabel("Y")
        return figure

    def _generate_points(self, start: float, stop: float, *, count: int) -> List[float]:
        """Create equidistant X values for plotting."""
        step = (stop - start) / max(count - 1, 1)
        return [start + step * i for i in range(count)]

    def _evaluate_series(self, expression: str, xs: Iterable[float]) -> List[float]:
        """Evaluate ``expression`` for each value in ``xs``."""
        values: List[float] = []
        for x_value in xs:
            try:
                y_value = self.calculator.evaluate_function(expression, x_value=x_value)
            except TI84Error:
                y_value = float("nan")
            values.append(y_value)
        return values

    def _annotate_intersections(self, axis, xs: List[float]) -> None:
        """Mark approximate intersection points between plotted equations."""
        if len(self.equations) < 2:
            return

        labels = sorted(self.equations)
        for i in range(len(labels)):
            for j in range(i + 1, len(labels)):
                expr_a = self.equations[labels[i]]
                expr_b = self.equations[labels[j]]
                intersections = self._find_intersections(expr_a, expr_b, xs)
                for x_val, y_val in intersections:
                    axis.plot(x_val, y_val, "o", color="red")
                    axis.annotate(
                        f"({x_val:.2f}, {y_val:.2f})",
                        (x_val, y_val),
                        textcoords="offset points",
                        xytext=(5, 5),
                        fontsize=8,
                    )

    def _find_intersections(
        self, expr_a: str, expr_b: str, xs: Iterable[float]
    ) -> List[Tuple[float, float]]:
        """Find approximate intersections between two expressions."""
        intersections: List[Tuple[float, float]] = []
        last_diff = None
        last_x = None
        last_y = None
        for x_value in xs:
            try:
                y_a = self.calculator.evaluate_function(expr_a, x_value=x_value)
                y_b = self.calculator.evaluate_function(expr_b, x_value=x_value)
            except TI84Error:
                continue
            diff = y_a - y_b
            if math.isnan(diff) or math.isinf(diff):
                continue
            if last_diff is not None and diff == 0:
                intersections.append((x_value, y_a))
            elif last_diff is not None and (diff > 0) != (last_diff > 0):
                # Linear interpolation for the root between the samples.
                proportion = abs(last_diff) / (abs(last_diff) + abs(diff))
                x_intersect = last_x + (x_value - last_x) * proportion
                y_intersect = last_y + (y_a - last_y) * proportion
                intersections.append((x_intersect, y_intersect))
            last_diff = diff
            last_x = x_value
            last_y = y_a
        return intersections


__all__ = ["GraphingEngine", "GraphWindow"]
