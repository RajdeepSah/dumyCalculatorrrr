"""Tkinter user interface for the TI-84 style calculator."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from typing import Dict, Optional

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from graphing_engine import GraphingEngine
from ti84_engine import TI84Engine, TI84Error


class CalculatorUI:
    """Build and manage the Tkinter interface for the calculator."""

    def __init__(self, master: tk.Tk):
        self.master = master
        self.master.title("TI-84 Style Calculator")
        self.master.configure(bg="#1f1f1f")
        self.master.resizable(False, False)

        self.engine = TI84Engine()
        self.graph_engine = GraphingEngine(self.engine)

        self.expression: str = ""
        self.display_var = tk.StringVar(value="0")

        self.buttons: Dict[str, tk.Button] = {}
        self._history_cursor: Optional[int] = None

        self._build_layout()
        self._refresh_history()
        self.master.bind("<Return>", lambda event: self._evaluate_expression())

    # ------------------------------------------------------------------ UI SETUP
    def _build_layout(self) -> None:
        """Assemble the display, history, and keypad sections."""
        outer = tk.Frame(self.master, bg="#0e0e0e", bd=8, relief=tk.RIDGE)
        outer.grid(row=0, column=0, padx=10, pady=10)

        display_frame = tk.Frame(outer, bg="#2d3b3b", bd=4, relief=tk.SUNKEN)
        display_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(0, 10))

        display_label = tk.Label(
            display_frame,
            textvariable=self.display_var,
            font=("Courier", 20),
            fg="#9dff91",
            bg="#1b2a2a",
            anchor="e",
            width=28,
            height=2,
        )
        display_label.pack(fill=tk.BOTH, expand=True)

        history_frame = tk.Frame(outer, bg="#111111", bd=4, relief=tk.SUNKEN)
        history_frame.grid(row=1, column=1, sticky="nsew", padx=(10, 0))

        history_title = tk.Label(
            history_frame,
            text="History",
            bg="#222222",
            fg="#eeeeee",
            font=("Arial", 10, "bold"),
        )
        history_title.pack(fill=tk.X)

        self.history_box = tk.Listbox(
            history_frame,
            bg="#0f1c1c",
            fg="#90f7ff",
            font=("Courier", 10),
            height=16,
        )
        self.history_box.pack(fill=tk.BOTH, expand=True)

        keypad_frame = tk.Frame(outer, bg="#111111")
        keypad_frame.grid(row=1, column=0, sticky="nsew")

        self._create_top_keys(keypad_frame)
        self._create_keypad(keypad_frame)

    def _create_top_keys(self, parent: tk.Frame) -> None:
        """Create the row of mode/graph related buttons."""
        top_buttons = [
            ("Y=", self._open_equation_editor),
            ("WINDOW", self._open_window_editor),
            ("ZOOM", lambda: messagebox.showinfo("Zoom", "Zoom presets are not implemented.")),
            ("TRACE", lambda: messagebox.showinfo("Trace", "Trace mode is not implemented.")),
            ("GRAPH", self._show_graph),
        ]
        row = tk.Frame(parent, bg="#111111")
        row.grid(row=0, column=0, columnspan=5, pady=(0, 6))
        for idx, (label, command) in enumerate(top_buttons):
            button = tk.Button(
                row,
                text=label,
                width=7,
                height=2,
                bg="#3a3a3a",
                fg="white",
                command=lambda cmd=command, lbl=label: self._on_button_press(lbl, cmd=cmd),
            )
            button.grid(row=0, column=idx, padx=2)
            self.buttons[label] = button

    def _create_keypad(self, parent: tk.Frame) -> None:
        """Create the remainder of the keypad following a TI-84 layout."""
        layout = [
            [
                ("2ND", lambda: messagebox.showinfo("2ND", "Secondary functions are not implemented.")),
                ("MODE", lambda: messagebox.showinfo("MODE", "Mode selection is not implemented.")),
                ("DEL", self._backspace),
                ("ALPHA", lambda: messagebox.showinfo("ALPHA", "Alpha input is not implemented.")),
                ("X,T,θ,n", lambda: self._append_to_expression("x")),
            ],
            [
                ("MATH", lambda: messagebox.showinfo("MATH", "Math menu is not implemented.")),
                ("APPS", lambda: messagebox.showinfo("APPS", "Apps are not implemented.")),
                ("PRGM", lambda: messagebox.showinfo("PRGM", "Programs are not implemented.")),
                ("VARS", lambda: messagebox.showinfo("VARS", "Vars menu is not implemented.")),
                ("CLEAR", self._clear_expression),
            ],
            [
                ("SIN", lambda: self._append_to_expression("sin(")),
                ("COS", lambda: self._append_to_expression("cos(")),
                ("TAN", lambda: self._append_to_expression("tan(")),
                ("^", lambda: self._append_to_expression("^")),
                ("√", lambda: self._append_to_expression("√(")),
            ],
            [
                ("7", lambda: self._append_to_expression("7")),
                ("8", lambda: self._append_to_expression("8")),
                ("9", lambda: self._append_to_expression("9")),
                ("÷", lambda: self._append_to_expression("÷")),
                ("LOG", lambda: self._append_to_expression("log(")),
            ],
            [
                ("4", lambda: self._append_to_expression("4")),
                ("5", lambda: self._append_to_expression("5")),
                ("6", lambda: self._append_to_expression("6")),
                ("×", lambda: self._append_to_expression("×")),
                ("LN", lambda: self._append_to_expression("ln(")),
            ],
            [
                ("1", lambda: self._append_to_expression("1")),
                ("2", lambda: self._append_to_expression("2")),
                ("3", lambda: self._append_to_expression("3")),
                ("-", lambda: self._append_to_expression("-")),
                ("π", lambda: self._append_to_expression("π")),
            ],
            [
                ("0", lambda: self._append_to_expression("0")),
                (".", lambda: self._append_to_expression(".")),
                ("(-)", lambda: self._append_to_expression("-")),
                ("+", lambda: self._append_to_expression("+")),
                ("e", lambda: self._append_to_expression("e")),
            ],
            [
                ("(", lambda: self._append_to_expression("(")),
                (")", lambda: self._append_to_expression(")")),
                (",", lambda: self._append_to_expression(",")),
                ("x^-1", lambda: self._append_to_expression("^(-1)")),
                ("x^2", lambda: self._append_to_expression("^(2)")),
            ],
            [
                ("ANS", lambda: self._append_to_expression("Ans")),
                ("|x|", lambda: self._append_to_expression("abs(")),
                ("!", lambda: self._append_to_expression("!")),
                ("STO→", lambda: messagebox.showinfo("Store", "Variable storage is not implemented.")),
                ("EE", lambda: self._append_to_expression("E")),
            ],
            [
                ("M+", self._memory_add),
                ("M-", self._memory_subtract),
                ("MR", self._memory_recall),
                ("MC", self._memory_clear),
                ("=", self._evaluate_expression),
            ],
            [
                ("◄", lambda: messagebox.showinfo("Arrow", "Horizontal navigation is not implemented.")),
                ("▲", self._history_previous),
                ("▼", self._history_next),
                ("►", lambda: messagebox.showinfo("Arrow", "Horizontal navigation is not implemented.")),
                ("ENTER", self._evaluate_expression),
            ],
        ]

        for row_index, row in enumerate(layout, start=1):
            for column_index, (label, command) in enumerate(row):
                button = tk.Button(
                    parent,
                    text=label,
                    width=5,
                    height=2,
                    bg="#2a2a2a",
                    fg="white",
                    command=lambda cmd=command, lbl=label: self._on_button_press(lbl, cmd=cmd),
                )
                button.grid(row=row_index, column=column_index, padx=2, pady=2)
                self.buttons[label] = button

    # ------------------------------------------------------------------ BUTTON HANDLERS
    def _on_button_press(self, label: str, *, cmd) -> None:
        """Highlight the pressed button then execute its command."""
        button = self.buttons.get(label)
        if button is not None:
            original = button.cget("bg")
            button.configure(bg="#5a5a5a")
            self.master.after(120, lambda: button.configure(bg=original))
        cmd()

    def _append_to_expression(self, text: str) -> None:
        """Append ``text`` to the current expression and update the display."""
        self._history_cursor = None
        self.expression += text
        self.display_var.set(self.expression)

    def _clear_expression(self) -> None:
        """Reset the expression and display to zero."""
        self._history_cursor = None
        self.expression = ""
        self.display_var.set("0")

    def _backspace(self) -> None:
        """Remove the last character from the expression."""
        self._history_cursor = None
        self.expression = self.expression[:-1]
        self.display_var.set(self.expression or "0")

    def _evaluate_expression(self) -> None:
        """Evaluate the current expression and update the display/history."""
        if not self.expression:
            return
        try:
            result = self.engine.evaluate(self.expression)
        except TI84Error as error:
            self.display_var.set(error.args[0])
        else:
            self.display_var.set(result.value)
            self.expression = result.value
            self._history_cursor = None
            self._refresh_history()

    # ------------------------------------------------------------------ MEMORY SUPPORT
    def _memory_add(self) -> None:
        """Add the evaluated expression to memory (M+)."""
        value = self._evaluate_safely()
        if value is not None:
            self.engine.add_to_memory(value)
            messagebox.showinfo("Memory", f"M = {self.engine.recall_memory():.6g}")

    def _memory_subtract(self) -> None:
        """Subtract the evaluated expression from memory (M-)."""
        value = self._evaluate_safely()
        if value is not None:
            self.engine.subtract_from_memory(value)
            messagebox.showinfo("Memory", f"M = {self.engine.recall_memory():.6g}")

    def _memory_recall(self) -> None:
        """Recall the memory value and append it to the expression."""
        self._append_to_expression(str(self.engine.recall_memory()))

    def _memory_clear(self) -> None:
        """Clear the calculator memory."""
        self.engine.clear_memory()
        messagebox.showinfo("Memory", "Memory cleared.")

    def _evaluate_safely(self) -> Optional[float]:
        """Return the numeric value of the current expression without updating UI."""
        if not self.expression:
            return None
        try:
            result = self.engine.evaluate(self.expression)
        except TI84Error as error:
            self.display_var.set(error.args[0])
            return None
        else:
            self.expression = result.value
            self.display_var.set(result.value)
            self._history_cursor = None
            self._refresh_history()
            return float(result.value)

    # ------------------------------------------------------------------ HISTORY
    def _refresh_history(self) -> None:
        """Update the history listbox with engine history."""
        self.history_box.delete(0, tk.END)
        for item in self.engine.history[::-1]:
            self.history_box.insert(tk.END, f"{item.expression} = {item.value}")

    def _history_previous(self) -> None:
        """Recall the previous calculation from history."""
        if not self.engine.history:
            return
        if self._history_cursor is None:
            self._history_cursor = len(self.engine.history) - 1
        else:
            self._history_cursor = max(0, self._history_cursor - 1)
        item = self.engine.history[self._history_cursor]
        self.expression = item.expression
        self.display_var.set(self.expression)

    def _history_next(self) -> None:
        """Move forward in the history list."""
        if self._history_cursor is None:
            return
        if self._history_cursor >= len(self.engine.history) - 1:
            self._history_cursor = None
            self.expression = ""
            self.display_var.set("0")
            return
        self._history_cursor += 1
        item = self.engine.history[self._history_cursor]
        self.expression = item.expression
        self.display_var.set(self.expression)

    # ------------------------------------------------------------------ GRAPHING WINDOWS
    def _open_equation_editor(self) -> None:
        """Open a dialog allowing the user to edit graph equations."""
        top = tk.Toplevel(self.master)
        top.title("Y=")
        top.configure(bg="#1f1f1f")

        entries: Dict[str, tk.Entry] = {}
        for idx, label in enumerate(["Y1", "Y2", "Y3", "Y4", "Y5", "Y6"], start=0):
            tk.Label(top, text=f"{label} =", bg="#1f1f1f", fg="white").grid(
                row=idx, column=0, sticky="e", padx=5, pady=4
            )
            entry = tk.Entry(top, width=25)
            entry.grid(row=idx, column=1, padx=5, pady=4)
            entry.insert(0, self.graph_engine.equations.get(label, ""))
            entries[label] = entry

        def save_equations() -> None:
            for label, entry in entries.items():
                self.graph_engine.set_equation(label, entry.get())
            top.destroy()

        tk.Button(top, text="OK", command=save_equations).grid(
            row=len(entries), column=0, columnspan=2, pady=8
        )

    def _open_window_editor(self) -> None:
        """Open a dialog for adjusting the graph window."""
        top = tk.Toplevel(self.master)
        top.title("Window")
        top.configure(bg="#1f1f1f")

        labels = ["Xmin", "Xmax", "Ymin", "Ymax"]
        fields: Dict[str, tk.Entry] = {}
        current = self.graph_engine.window
        values = {
            "Xmin": current.xmin,
            "Xmax": current.xmax,
            "Ymin": current.ymin,
            "Ymax": current.ymax,
        }
        for idx, label in enumerate(labels):
            tk.Label(top, text=label, bg="#1f1f1f", fg="white").grid(
                row=idx, column=0, sticky="e", padx=5, pady=4
            )
            entry = tk.Entry(top, width=15)
            entry.grid(row=idx, column=1, padx=5, pady=4)
            entry.insert(0, str(values[label]))
            fields[label] = entry

        def apply_window() -> None:
            try:
                xmin = float(fields["Xmin"].get())
                xmax = float(fields["Xmax"].get())
                ymin = float(fields["Ymin"].get())
                ymax = float(fields["Ymax"].get())
                self.graph_engine.set_window(xmin, xmax, ymin, ymax)
            except (ValueError, TI84Error):
                messagebox.showerror("Window", "Invalid window settings.")
            else:
                top.destroy()

        tk.Button(top, text="Apply", command=apply_window).grid(
            row=len(labels), column=0, columnspan=2, pady=8
        )

    def _show_graph(self) -> None:
        """Render the graph and show it in a new window."""
        try:
            figure = self.graph_engine.plot()
        except TI84Error as error:
            messagebox.showerror("Graph", error.args[0])
            return

        top = tk.Toplevel(self.master)
        top.title("Graph")
        top.configure(bg="#1f1f1f")

        canvas = FigureCanvasTkAgg(figure, master=top)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        def on_close() -> None:
            # Explicitly close the matplotlib figure to free resources.
            figure.clf()
            top.destroy()

        top.protocol("WM_DELETE_WINDOW", on_close)


def run_app() -> None:
    """Entry point to start the calculator application."""
    root = tk.Tk()
    CalculatorUI(root)
    root.mainloop()


__all__ = ["CalculatorUI", "run_app"]
