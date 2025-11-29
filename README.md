# PostScript Interpreter

A Python implementation of a PostScript interpreter with parsing and execution support.

## Features

- **Lexer/Tokenizer**: Converts PostScript source code into tokens
- **Parser**: Creates an abstract syntax representation from tokens
- **Interpreter**: Stack-based execution engine

### Supported Operations

- **Arithmetic**: `add`, `sub`, `mul`, `div`, `idiv`, `mod`, `neg`, `abs`, `sqrt`, `ceiling`, `floor`, `round`, `truncate`
- **Stack Manipulation**: `pop`, `exch`, `dup`, `copy`, `index`, `roll`, `clear`, `count`, `mark`, `cleartomark`
- **Comparison**: `eq`, `ne`, `lt`, `le`, `gt`, `ge`
- **Boolean**: `and`, `or`, `not`, `xor`, `true`, `false`
- **Control Flow**: `if`, `ifelse`, `for`, `repeat`, `loop`, `exit`, `exec`, `stopped`, `stop`
- **Dictionary**: `def`, `load`, `store`, `begin`, `end`, `dict`, `currentdict`
- **Array/String**: `array`, `length`, `get`, `put`, `getinterval`, `putinterval`, `forall`, `aload`, `astore`, `string`, `cvs`
- **Type**: `type`, `cvx`, `cvlit`
- **I/O**: `print`, `=`, `==`, `pstack`

## Installation

```bash
pip install -e ".[dev]"
```

## Usage

```python
from postscript_interpreter import Interpreter

interp = Interpreter()
interp.run("3 5 add 2 mul")
print(interp.get_stack())  # [16]
```

### Example: Factorial

```python
interp = Interpreter()
interp.run("""
    /factorial {
        dup 1 le
        { pop 1 }
        { dup 1 sub factorial mul }
        ifelse
    } def
    5 factorial
""")
print(interp.get_stack())  # [120]
```

## Testing

```bash
pytest tests/
```
