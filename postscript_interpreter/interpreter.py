"""PostScript interpreter with stack-based execution."""

from typing import Dict, List, Callable, Any, Optional
from .lexer import Lexer, LexerError
from .parser import Parser, Procedure, LiteralName, ExecutableName, ParserError


class InterpreterError(Exception):
    """Exception raised for interpreter errors."""
    pass


class Interpreter:
    """PostScript interpreter with parsing and execution."""

    def __init__(self):
        """Initialize the interpreter."""
        self.operand_stack: List[Any] = []
        self.dictionary_stack: List[Dict[str, Any]] = [{}]  # Start with one user dict
        self._init_system_dict()

    def _init_system_dict(self) -> None:
        """Initialize system dictionary with built-in operators."""
        system_dict = {}

        # Arithmetic operators
        system_dict['add'] = self._op_add
        system_dict['sub'] = self._op_sub
        system_dict['mul'] = self._op_mul
        system_dict['div'] = self._op_div
        system_dict['idiv'] = self._op_idiv
        system_dict['mod'] = self._op_mod
        system_dict['neg'] = self._op_neg
        system_dict['abs'] = self._op_abs
        system_dict['ceiling'] = self._op_ceiling
        system_dict['floor'] = self._op_floor
        system_dict['round'] = self._op_round
        system_dict['truncate'] = self._op_truncate
        system_dict['sqrt'] = self._op_sqrt

        # Stack manipulation
        system_dict['pop'] = self._op_pop
        system_dict['exch'] = self._op_exch
        system_dict['dup'] = self._op_dup
        system_dict['copy'] = self._op_copy
        system_dict['index'] = self._op_index
        system_dict['roll'] = self._op_roll
        system_dict['clear'] = self._op_clear
        system_dict['count'] = self._op_count
        system_dict['mark'] = self._op_mark
        system_dict['cleartomark'] = self._op_cleartomark

        # Comparison operators
        system_dict['eq'] = self._op_eq
        system_dict['ne'] = self._op_ne
        system_dict['lt'] = self._op_lt
        system_dict['le'] = self._op_le
        system_dict['gt'] = self._op_gt
        system_dict['ge'] = self._op_ge

        # Boolean operators
        system_dict['and'] = self._op_and
        system_dict['or'] = self._op_or
        system_dict['not'] = self._op_not
        system_dict['xor'] = self._op_xor
        system_dict['true'] = True
        system_dict['false'] = False

        # Control flow
        system_dict['if'] = self._op_if
        system_dict['ifelse'] = self._op_ifelse
        system_dict['for'] = self._op_for
        system_dict['repeat'] = self._op_repeat
        system_dict['loop'] = self._op_loop
        system_dict['exit'] = self._op_exit
        system_dict['exec'] = self._op_exec
        system_dict['stopped'] = self._op_stopped
        system_dict['stop'] = self._op_stop

        # Dictionary operations
        system_dict['def'] = self._op_def
        system_dict['load'] = self._op_load
        system_dict['store'] = self._op_store
        system_dict['begin'] = self._op_begin
        system_dict['end'] = self._op_end
        system_dict['dict'] = self._op_dict
        system_dict['currentdict'] = self._op_currentdict

        # Array operations
        system_dict['array'] = self._op_array
        system_dict['length'] = self._op_length
        system_dict['get'] = self._op_get
        system_dict['put'] = self._op_put
        system_dict['getinterval'] = self._op_getinterval
        system_dict['putinterval'] = self._op_putinterval
        system_dict['forall'] = self._op_forall
        system_dict['aload'] = self._op_aload
        system_dict['astore'] = self._op_astore

        # String operations
        system_dict['string'] = self._op_string
        system_dict['cvs'] = self._op_cvs

        # Type checking
        system_dict['type'] = self._op_type
        system_dict['cvx'] = self._op_cvx
        system_dict['cvlit'] = self._op_cvlit

        # I/O
        system_dict['print'] = self._op_print
        system_dict['='] = self._op_equals
        system_dict['=='] = self._op_equalsequals
        system_dict['pstack'] = self._op_pstack

        # Insert system dict at bottom of stack
        self.dictionary_stack.insert(0, system_dict)

    # Arithmetic operators
    def _op_add(self) -> None:
        b = self._pop_number()
        a = self._pop_number()
        self.operand_stack.append(a + b)

    def _op_sub(self) -> None:
        b = self._pop_number()
        a = self._pop_number()
        self.operand_stack.append(a - b)

    def _op_mul(self) -> None:
        b = self._pop_number()
        a = self._pop_number()
        self.operand_stack.append(a * b)

    def _op_div(self) -> None:
        b = self._pop_number()
        a = self._pop_number()
        if b == 0:
            raise InterpreterError("Division by zero")
        self.operand_stack.append(a / b)

    def _op_idiv(self) -> None:
        b = self._pop_int()
        a = self._pop_int()
        if b == 0:
            raise InterpreterError("Division by zero")
        self.operand_stack.append(int(a // b))

    def _op_mod(self) -> None:
        b = self._pop_int()
        a = self._pop_int()
        if b == 0:
            raise InterpreterError("Division by zero")
        self.operand_stack.append(a % b)

    def _op_neg(self) -> None:
        a = self._pop_number()
        self.operand_stack.append(-a)

    def _op_abs(self) -> None:
        a = self._pop_number()
        self.operand_stack.append(abs(a))

    def _op_ceiling(self) -> None:
        import math
        a = self._pop_number()
        self.operand_stack.append(float(math.ceil(a)))

    def _op_floor(self) -> None:
        import math
        a = self._pop_number()
        self.operand_stack.append(float(math.floor(a)))

    def _op_round(self) -> None:
        a = self._pop_number()
        self.operand_stack.append(float(round(a)))

    def _op_truncate(self) -> None:
        import math
        a = self._pop_number()
        self.operand_stack.append(float(math.trunc(a)))

    def _op_sqrt(self) -> None:
        import math
        a = self._pop_number()
        if a < 0:
            raise InterpreterError("sqrt: negative number")
        self.operand_stack.append(math.sqrt(a))

    # Stack manipulation
    def _op_pop(self) -> None:
        self._pop()

    def _op_exch(self) -> None:
        if len(self.operand_stack) < 2:
            raise InterpreterError("exch: stack underflow")
        self.operand_stack[-1], self.operand_stack[-2] = \
            self.operand_stack[-2], self.operand_stack[-1]

    def _op_dup(self) -> None:
        if len(self.operand_stack) < 1:
            raise InterpreterError("dup: stack underflow")
        self.operand_stack.append(self.operand_stack[-1])

    def _op_copy(self) -> None:
        n = self._pop_int()
        if n < 0 or n > len(self.operand_stack):
            raise InterpreterError("copy: invalid count")
        if n > 0:
            items = self.operand_stack[-n:]
            self.operand_stack.extend(items)

    def _op_index(self) -> None:
        n = self._pop_int()
        if n < 0 or n >= len(self.operand_stack):
            raise InterpreterError("index: invalid index")
        self.operand_stack.append(self.operand_stack[-(n + 1)])

    def _op_roll(self) -> None:
        j = self._pop_int()
        n = self._pop_int()
        if n < 0:
            raise InterpreterError("roll: negative count")
        if n == 0 or j == 0:
            return
        if n > len(self.operand_stack):
            raise InterpreterError("roll: stack underflow")
        # Get the top n elements
        items = self.operand_stack[-n:]
        # Roll them: positive j moves top elements down
        j = j % n
        rolled = items[-j:] + items[:-j]
        self.operand_stack[-n:] = rolled

    def _op_clear(self) -> None:
        self.operand_stack.clear()

    def _op_count(self) -> None:
        self.operand_stack.append(len(self.operand_stack))

    def _op_mark(self) -> None:
        self.operand_stack.append(Mark())

    def _op_cleartomark(self) -> None:
        while self.operand_stack:
            item = self.operand_stack.pop()
            if isinstance(item, Mark):
                return
        raise InterpreterError("cleartomark: no mark found")

    # Comparison operators
    def _op_eq(self) -> None:
        b = self._pop()
        a = self._pop()
        self.operand_stack.append(a == b)

    def _op_ne(self) -> None:
        b = self._pop()
        a = self._pop()
        self.operand_stack.append(a != b)

    def _op_lt(self) -> None:
        b = self._pop()
        a = self._pop()
        self.operand_stack.append(a < b)

    def _op_le(self) -> None:
        b = self._pop()
        a = self._pop()
        self.operand_stack.append(a <= b)

    def _op_gt(self) -> None:
        b = self._pop()
        a = self._pop()
        self.operand_stack.append(a > b)

    def _op_ge(self) -> None:
        b = self._pop()
        a = self._pop()
        self.operand_stack.append(a >= b)

    # Boolean operators
    def _op_and(self) -> None:
        b = self._pop()
        a = self._pop()
        if isinstance(a, bool) and isinstance(b, bool):
            self.operand_stack.append(a and b)
        elif isinstance(a, int) and isinstance(b, int):
            self.operand_stack.append(a & b)
        else:
            raise InterpreterError("and: type mismatch")

    def _op_or(self) -> None:
        b = self._pop()
        a = self._pop()
        if isinstance(a, bool) and isinstance(b, bool):
            self.operand_stack.append(a or b)
        elif isinstance(a, int) and isinstance(b, int):
            self.operand_stack.append(a | b)
        else:
            raise InterpreterError("or: type mismatch")

    def _op_not(self) -> None:
        a = self._pop()
        if isinstance(a, bool):
            self.operand_stack.append(not a)
        elif isinstance(a, int):
            self.operand_stack.append(~a)
        else:
            raise InterpreterError("not: type mismatch")

    def _op_xor(self) -> None:
        b = self._pop()
        a = self._pop()
        if isinstance(a, bool) and isinstance(b, bool):
            self.operand_stack.append(a != b)
        elif isinstance(a, int) and isinstance(b, int):
            self.operand_stack.append(a ^ b)
        else:
            raise InterpreterError("xor: type mismatch")

    # Control flow
    def _op_if(self) -> None:
        proc = self._pop_procedure()
        cond = self._pop_bool()
        if cond:
            self._execute_procedure(proc)

    def _op_ifelse(self) -> None:
        false_proc = self._pop_procedure()
        true_proc = self._pop_procedure()
        cond = self._pop_bool()
        if cond:
            self._execute_procedure(true_proc)
        else:
            self._execute_procedure(false_proc)

    def _op_for(self) -> None:
        proc = self._pop_procedure()
        limit = self._pop_number()
        increment = self._pop_number()
        initial = self._pop_number()

        current = initial
        try:
            if increment > 0:
                while current <= limit:
                    self.operand_stack.append(current)
                    self._execute_procedure(proc)
                    current += increment
            else:
                while current >= limit:
                    self.operand_stack.append(current)
                    self._execute_procedure(proc)
                    current += increment
        except ExitException:
            pass

    def _op_repeat(self) -> None:
        proc = self._pop_procedure()
        count = self._pop_int()
        if count < 0:
            raise InterpreterError("repeat: negative count")
        try:
            for _ in range(count):
                self._execute_procedure(proc)
        except ExitException:
            pass

    def _op_loop(self) -> None:
        proc = self._pop_procedure()
        try:
            while True:
                self._execute_procedure(proc)
        except ExitException:
            pass

    def _op_exit(self) -> None:
        raise ExitException()

    def _op_exec(self) -> None:
        obj = self._pop()
        self._execute_object(obj)

    def _op_stopped(self) -> None:
        proc = self._pop_procedure()
        try:
            self._execute_procedure(proc)
            self.operand_stack.append(False)
        except StopException:
            self.operand_stack.append(True)

    def _op_stop(self) -> None:
        raise StopException()

    # Dictionary operations
    def _op_def(self) -> None:
        value = self._pop()
        key = self._pop_literal_name()
        self.dictionary_stack[-1][key] = value

    def _op_load(self) -> None:
        key = self._pop_literal_name()
        value = self._lookup(key)
        if value is None:
            raise InterpreterError(f"load: undefined name '{key}'")
        self.operand_stack.append(value)

    def _op_store(self) -> None:
        value = self._pop()
        key = self._pop_literal_name()
        # Store in first dict that has the key, or current dict
        for d in reversed(self.dictionary_stack):
            if key in d:
                d[key] = value
                return
        self.dictionary_stack[-1][key] = value

    def _op_begin(self) -> None:
        d = self._pop()
        if not isinstance(d, dict):
            raise InterpreterError("begin: not a dictionary")
        self.dictionary_stack.append(d)

    def _op_end(self) -> None:
        if len(self.dictionary_stack) <= 2:  # system dict + one user dict
            raise InterpreterError("end: dictionary stack underflow")
        self.dictionary_stack.pop()

    def _op_dict(self) -> None:
        n = self._pop_int()
        self.operand_stack.append({})

    def _op_currentdict(self) -> None:
        self.operand_stack.append(self.dictionary_stack[-1])

    # Array operations
    def _op_array(self) -> None:
        n = self._pop_int()
        if n < 0:
            raise InterpreterError("array: negative size")
        self.operand_stack.append([None] * n)

    def _op_length(self) -> None:
        obj = self._pop()
        if isinstance(obj, (list, str, dict)):
            self.operand_stack.append(len(obj))
        else:
            raise InterpreterError("length: invalid type")

    def _op_get(self) -> None:
        index = self._pop()
        obj = self._pop()
        if isinstance(obj, list):
            if not isinstance(index, int):
                raise InterpreterError("get: index must be integer for array")
            if index < 0 or index >= len(obj):
                raise InterpreterError("get: index out of range")
            self.operand_stack.append(obj[index])
        elif isinstance(obj, str):
            if not isinstance(index, int):
                raise InterpreterError("get: index must be integer for string")
            if index < 0 or index >= len(obj):
                raise InterpreterError("get: index out of range")
            self.operand_stack.append(ord(obj[index]))
        elif isinstance(obj, dict):
            self.operand_stack.append(obj[index])
        else:
            raise InterpreterError("get: invalid type")

    def _op_put(self) -> None:
        value = self._pop()
        index = self._pop()
        obj = self._pop()
        if isinstance(obj, list):
            if not isinstance(index, int):
                raise InterpreterError("put: index must be integer for array")
            if index < 0 or index >= len(obj):
                raise InterpreterError("put: index out of range")
            obj[index] = value
        elif isinstance(obj, dict):
            obj[index] = value
        else:
            raise InterpreterError("put: invalid type")

    def _op_getinterval(self) -> None:
        count = self._pop_int()
        index = self._pop_int()
        obj = self._pop()
        if isinstance(obj, list):
            if index < 0 or index + count > len(obj):
                raise InterpreterError("getinterval: range out of bounds")
            self.operand_stack.append(obj[index:index + count])
        elif isinstance(obj, str):
            if index < 0 or index + count > len(obj):
                raise InterpreterError("getinterval: range out of bounds")
            self.operand_stack.append(obj[index:index + count])
        else:
            raise InterpreterError("getinterval: invalid type")

    def _op_putinterval(self) -> None:
        source = self._pop()
        index = self._pop_int()
        dest = self._pop()
        if isinstance(dest, list) and isinstance(source, list):
            if index < 0 or index + len(source) > len(dest):
                raise InterpreterError("putinterval: range out of bounds")
            for i, v in enumerate(source):
                dest[index + i] = v
        else:
            raise InterpreterError("putinterval: invalid type")

    def _op_forall(self) -> None:
        proc = self._pop_procedure()
        obj = self._pop()
        try:
            if isinstance(obj, list):
                for item in obj:
                    self.operand_stack.append(item)
                    self._execute_procedure(proc)
            elif isinstance(obj, str):
                for char in obj:
                    self.operand_stack.append(ord(char))
                    self._execute_procedure(proc)
            elif isinstance(obj, dict):
                for key, value in obj.items():
                    self.operand_stack.append(key)
                    self.operand_stack.append(value)
                    self._execute_procedure(proc)
            else:
                raise InterpreterError("forall: invalid type")
        except ExitException:
            pass

    def _op_aload(self) -> None:
        arr = self._pop()
        if not isinstance(arr, list):
            raise InterpreterError("aload: not an array")
        for item in arr:
            self.operand_stack.append(item)
        self.operand_stack.append(arr)

    def _op_astore(self) -> None:
        arr = self._pop()
        if not isinstance(arr, list):
            raise InterpreterError("astore: not an array")
        n = len(arr)
        if len(self.operand_stack) < n:
            raise InterpreterError("astore: stack underflow")
        for i in range(n - 1, -1, -1):
            arr[i] = self.operand_stack.pop()
        self.operand_stack.append(arr)

    # String operations
    def _op_string(self) -> None:
        n = self._pop_int()
        if n < 0:
            raise InterpreterError("string: negative size")
        self.operand_stack.append('\0' * n)

    def _op_cvs(self) -> None:
        s = self._pop()
        obj = self._pop()
        result = str(obj)
        self.operand_stack.append(result)

    # Type checking
    def _op_type(self) -> None:
        obj = self._pop()
        if isinstance(obj, bool):
            self.operand_stack.append("booleantype")
        elif isinstance(obj, int):
            self.operand_stack.append("integertype")
        elif isinstance(obj, float):
            self.operand_stack.append("realtype")
        elif isinstance(obj, str):
            self.operand_stack.append("stringtype")
        elif isinstance(obj, list):
            self.operand_stack.append("arraytype")
        elif isinstance(obj, dict):
            self.operand_stack.append("dicttype")
        elif isinstance(obj, Procedure):
            self.operand_stack.append("arraytype")
        elif isinstance(obj, LiteralName):
            self.operand_stack.append("nametype")
        elif isinstance(obj, Mark):
            self.operand_stack.append("marktype")
        elif callable(obj):
            self.operand_stack.append("operatortype")
        else:
            self.operand_stack.append("nulltype")

    def _op_cvx(self) -> None:
        obj = self._pop()
        if isinstance(obj, LiteralName):
            self.operand_stack.append(ExecutableName(obj.name))
        elif isinstance(obj, list):
            self.operand_stack.append(Procedure(obj))
        else:
            self.operand_stack.append(obj)

    def _op_cvlit(self) -> None:
        obj = self._pop()
        if isinstance(obj, ExecutableName):
            self.operand_stack.append(LiteralName(obj.name))
        elif isinstance(obj, Procedure):
            self.operand_stack.append(obj.body)
        else:
            self.operand_stack.append(obj)

    # I/O
    def _op_print(self) -> None:
        s = self._pop()
        if not isinstance(s, str):
            raise InterpreterError("print: not a string")
        print(s, end='')

    def _op_equals(self) -> None:
        obj = self._pop()
        print(self._format_object(obj))

    def _op_equalsequals(self) -> None:
        obj = self._pop()
        print(self._format_object_detailed(obj))

    def _op_pstack(self) -> None:
        for obj in reversed(self.operand_stack):
            print(self._format_object_detailed(obj))

    # Helper methods
    def _pop(self) -> Any:
        if not self.operand_stack:
            raise InterpreterError("Stack underflow")
        return self.operand_stack.pop()

    def _pop_number(self) -> float:
        obj = self._pop()
        if isinstance(obj, (int, float)):
            return obj
        raise InterpreterError(f"Expected number, got {type(obj).__name__}")

    def _pop_int(self) -> int:
        obj = self._pop()
        if isinstance(obj, int) and not isinstance(obj, bool):
            return obj
        if isinstance(obj, float) and obj == int(obj):
            return int(obj)
        raise InterpreterError(f"Expected integer, got {type(obj).__name__}")

    def _pop_bool(self) -> bool:
        obj = self._pop()
        if isinstance(obj, bool):
            return obj
        raise InterpreterError(f"Expected boolean, got {type(obj).__name__}")

    def _pop_procedure(self) -> Procedure:
        obj = self._pop()
        if isinstance(obj, Procedure):
            return obj
        raise InterpreterError(f"Expected procedure, got {type(obj).__name__}")

    def _pop_literal_name(self) -> str:
        obj = self._pop()
        if isinstance(obj, LiteralName):
            return obj.name
        raise InterpreterError(f"Expected literal name, got {type(obj).__name__}")

    def _lookup(self, name: str) -> Optional[Any]:
        """Look up a name in the dictionary stack."""
        for d in reversed(self.dictionary_stack):
            if name in d:
                return d[name]
        return None

    def _execute_procedure(self, proc: Procedure) -> None:
        """Execute a procedure."""
        for obj in proc.body:
            self._execute_object(obj)

    def _execute_object(self, obj: Any) -> None:
        """Execute a parsed object."""
        if isinstance(obj, (int, float, str, bool)):
            self.operand_stack.append(obj)
        elif isinstance(obj, list):
            # Arrays are pushed literally
            self.operand_stack.append(obj)
        elif isinstance(obj, LiteralName):
            self.operand_stack.append(obj)
        elif isinstance(obj, Procedure):
            self.operand_stack.append(obj)
        elif isinstance(obj, ExecutableName):
            value = self._lookup(obj.name)
            if value is None:
                raise InterpreterError(f"Undefined name: {obj.name}")
            if callable(value):
                value()
            elif isinstance(value, Procedure):
                self._execute_procedure(value)
            else:
                self.operand_stack.append(value)
        else:
            self.operand_stack.append(obj)

    def _format_object(self, obj: Any) -> str:
        """Format an object for = operator."""
        if isinstance(obj, bool):
            return "true" if obj else "false"
        if isinstance(obj, LiteralName):
            return f"/{obj.name}"
        if isinstance(obj, ExecutableName):
            return obj.name
        if isinstance(obj, Procedure):
            return "--nostringval--"
        return str(obj)

    def _format_object_detailed(self, obj: Any) -> str:
        """Format an object for == operator."""
        if isinstance(obj, bool):
            return "true" if obj else "false"
        if isinstance(obj, LiteralName):
            return f"/{obj.name}"
        if isinstance(obj, ExecutableName):
            return obj.name
        if isinstance(obj, Procedure):
            items = ' '.join(self._format_object_detailed(x) for x in obj.body)
            return f"{{ {items} }}"
        if isinstance(obj, list):
            items = ' '.join(self._format_object_detailed(x) for x in obj)
            return f"[ {items} ]"
        if isinstance(obj, dict):
            return "-dict-"
        if isinstance(obj, Mark):
            return "-mark-"
        return str(obj)

    def run(self, source: str) -> None:
        """Parse and execute PostScript code."""
        parser = Parser(source)
        objects = parser.parse()
        for obj in objects:
            self._execute_object(obj)

    def get_stack(self) -> List[Any]:
        """Return a copy of the operand stack."""
        return self.operand_stack.copy()


class Mark:
    """Represents a mark on the stack."""
    def __repr__(self) -> str:
        return "-mark-"


class ExitException(Exception):
    """Exception raised by exit operator."""
    pass


class StopException(Exception):
    """Exception raised by stop operator."""
    pass
