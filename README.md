# dumyCalculatorrrr

AS it is named, dont expect too much, it's just practice

## Simple calculator (command line)

Run the calculator from the command line:

```bash
python simple_calculator.py
```

## TI-84 style desktop calculator

Install the UI dependencies (Tkinter ships with Python, but matplotlib is required for graphing):

```bash
pip install matplotlib
```

Then start the calculator application:

```bash
python main.py
```

The interface mimics a TI-84 layout, supports history, memory operations, trigonometric/logarithmic functions, and renders graphs using matplotlib.

## Simple calculator (web)

Open `index.html` in any modern browser or serve the project locally, for example:

```bash
python -m http.server
```

Then visit [http://localhost:8000](http://localhost:8000) and try the interactive interface.
