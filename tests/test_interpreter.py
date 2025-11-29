"""Tests for the PostScript interpreter."""

import pytest
from postscript_interpreter import Interpreter, Lexer, Parser
from postscript_interpreter.lexer import TokenType, LexerError
from postscript_interpreter.parser import ParserError, Procedure, LiteralName, ExecutableName
from postscript_interpreter.interpreter import InterpreterError


class TestLexer:
    """Tests for the Lexer class."""

    def test_number_tokens(self):
        """Test tokenizing numbers."""
        lexer = Lexer("42 3.14 -10 +5")
        tokens = list(lexer.tokenize())
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == 42
        assert tokens[1].type == TokenType.NUMBER
        assert tokens[1].value == 3.14
        assert tokens[2].type == TokenType.NUMBER
        assert tokens[2].value == -10
        assert tokens[3].type == TokenType.NUMBER
        assert tokens[3].value == 5

    def test_name_tokens(self):
        """Test tokenizing names."""
        lexer = Lexer("add sub mul div")
        tokens = list(lexer.tokenize())
        assert tokens[0].type == TokenType.NAME
        assert tokens[0].value == "add"
        assert tokens[1].type == TokenType.NAME
        assert tokens[1].value == "sub"

    def test_literal_name_tokens(self):
        """Test tokenizing literal names."""
        lexer = Lexer("/x /myvar /hello")
        tokens = list(lexer.tokenize())
        assert tokens[0].type == TokenType.LITERAL_NAME
        assert tokens[0].value == "x"
        assert tokens[1].type == TokenType.LITERAL_NAME
        assert tokens[1].value == "myvar"

    def test_string_tokens(self):
        """Test tokenizing strings."""
        lexer = Lexer("(hello world) (nested (parens))")
        tokens = list(lexer.tokenize())
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == "hello world"
        assert tokens[1].type == TokenType.STRING
        assert tokens[1].value == "nested (parens)"

    def test_brace_tokens(self):
        """Test tokenizing braces."""
        lexer = Lexer("{ } [ ]")
        tokens = list(lexer.tokenize())
        assert tokens[0].type == TokenType.LBRACE
        assert tokens[1].type == TokenType.RBRACE
        assert tokens[2].type == TokenType.LBRACKET
        assert tokens[3].type == TokenType.RBRACKET

    def test_comments(self):
        """Test that comments are skipped."""
        lexer = Lexer("1 % this is a comment\n2")
        tokens = list(lexer.tokenize())
        values = [t.value for t in tokens if t.type == TokenType.NUMBER]
        assert values == [1, 2]

    def test_unterminated_string(self):
        """Test error for unterminated string."""
        lexer = Lexer("(unterminated")
        with pytest.raises(LexerError):
            list(lexer.tokenize())


class TestParser:
    """Tests for the Parser class."""

    def test_parse_numbers(self):
        """Test parsing numbers."""
        parser = Parser("1 2 3")
        result = parser.parse()
        assert result == [1, 2, 3]

    def test_parse_literal_names(self):
        """Test parsing literal names."""
        parser = Parser("/x /y")
        result = parser.parse()
        assert isinstance(result[0], LiteralName)
        assert result[0].name == "x"

    def test_parse_executable_names(self):
        """Test parsing executable names."""
        parser = Parser("add sub")
        result = parser.parse()
        assert isinstance(result[0], ExecutableName)
        assert result[0].name == "add"

    def test_parse_procedure(self):
        """Test parsing procedures."""
        parser = Parser("{ 1 2 add }")
        result = parser.parse()
        assert len(result) == 1
        assert isinstance(result[0], Procedure)
        assert result[0].body[0] == 1
        assert result[0].body[1] == 2

    def test_parse_nested_procedure(self):
        """Test parsing nested procedures."""
        parser = Parser("{ { 1 } }")
        result = parser.parse()
        assert isinstance(result[0], Procedure)
        assert isinstance(result[0].body[0], Procedure)

    def test_parse_array(self):
        """Test parsing arrays."""
        parser = Parser("[1 2 3]")
        result = parser.parse()
        assert isinstance(result[0], list)
        assert result[0] == [1, 2, 3]

    def test_unterminated_procedure(self):
        """Test error for unterminated procedure."""
        parser = Parser("{ 1 2")
        with pytest.raises(ParserError):
            parser.parse()


class TestInterpreterArithmetic:
    """Tests for arithmetic operations."""

    def test_add(self):
        """Test add operator."""
        interp = Interpreter()
        interp.run("3 5 add")
        assert interp.get_stack() == [8]

    def test_sub(self):
        """Test sub operator."""
        interp = Interpreter()
        interp.run("10 3 sub")
        assert interp.get_stack() == [7]

    def test_mul(self):
        """Test mul operator."""
        interp = Interpreter()
        interp.run("4 5 mul")
        assert interp.get_stack() == [20]

    def test_div(self):
        """Test div operator."""
        interp = Interpreter()
        interp.run("10 4 div")
        assert interp.get_stack() == [2.5]

    def test_idiv(self):
        """Test idiv operator."""
        interp = Interpreter()
        interp.run("10 3 idiv")
        assert interp.get_stack() == [3]

    def test_mod(self):
        """Test mod operator."""
        interp = Interpreter()
        interp.run("10 3 mod")
        assert interp.get_stack() == [1]

    def test_neg(self):
        """Test neg operator."""
        interp = Interpreter()
        interp.run("5 neg")
        assert interp.get_stack() == [-5]

    def test_abs(self):
        """Test abs operator."""
        interp = Interpreter()
        interp.run("-5 abs")
        assert interp.get_stack() == [5]


class TestInterpreterStack:
    """Tests for stack manipulation."""

    def test_pop(self):
        """Test pop operator."""
        interp = Interpreter()
        interp.run("1 2 3 pop")
        assert interp.get_stack() == [1, 2]

    def test_exch(self):
        """Test exch operator."""
        interp = Interpreter()
        interp.run("1 2 exch")
        assert interp.get_stack() == [2, 1]

    def test_dup(self):
        """Test dup operator."""
        interp = Interpreter()
        interp.run("5 dup")
        assert interp.get_stack() == [5, 5]

    def test_copy(self):
        """Test copy operator."""
        interp = Interpreter()
        interp.run("1 2 3 2 copy")
        assert interp.get_stack() == [1, 2, 3, 2, 3]

    def test_index(self):
        """Test index operator."""
        interp = Interpreter()
        interp.run("1 2 3 0 index")
        assert interp.get_stack() == [1, 2, 3, 3]
        interp = Interpreter()
        interp.run("1 2 3 2 index")
        assert interp.get_stack() == [1, 2, 3, 1]

    def test_roll(self):
        """Test roll operator."""
        interp = Interpreter()
        interp.run("1 2 3 3 1 roll")
        assert interp.get_stack() == [3, 1, 2]

    def test_clear(self):
        """Test clear operator."""
        interp = Interpreter()
        interp.run("1 2 3 clear")
        assert interp.get_stack() == []

    def test_count(self):
        """Test count operator."""
        interp = Interpreter()
        interp.run("1 2 3 count")
        assert interp.get_stack() == [1, 2, 3, 3]


class TestInterpreterComparison:
    """Tests for comparison operations."""

    def test_eq(self):
        """Test eq operator."""
        interp = Interpreter()
        interp.run("5 5 eq")
        assert interp.get_stack() == [True]
        interp = Interpreter()
        interp.run("5 3 eq")
        assert interp.get_stack() == [False]

    def test_ne(self):
        """Test ne operator."""
        interp = Interpreter()
        interp.run("5 3 ne")
        assert interp.get_stack() == [True]

    def test_lt(self):
        """Test lt operator."""
        interp = Interpreter()
        interp.run("3 5 lt")
        assert interp.get_stack() == [True]

    def test_gt(self):
        """Test gt operator."""
        interp = Interpreter()
        interp.run("5 3 gt")
        assert interp.get_stack() == [True]


class TestInterpreterBoolean:
    """Tests for boolean operations."""

    def test_and(self):
        """Test and operator."""
        interp = Interpreter()
        interp.run("true true and")
        assert interp.get_stack() == [True]
        interp = Interpreter()
        interp.run("true false and")
        assert interp.get_stack() == [False]

    def test_or(self):
        """Test or operator."""
        interp = Interpreter()
        interp.run("true false or")
        assert interp.get_stack() == [True]

    def test_not(self):
        """Test not operator."""
        interp = Interpreter()
        interp.run("true not")
        assert interp.get_stack() == [False]


class TestInterpreterControlFlow:
    """Tests for control flow operations."""

    def test_if_true(self):
        """Test if operator with true condition."""
        interp = Interpreter()
        interp.run("true { 42 } if")
        assert interp.get_stack() == [42]

    def test_if_false(self):
        """Test if operator with false condition."""
        interp = Interpreter()
        interp.run("false { 42 } if")
        assert interp.get_stack() == []

    def test_ifelse_true(self):
        """Test ifelse operator with true condition."""
        interp = Interpreter()
        interp.run("true { 1 } { 2 } ifelse")
        assert interp.get_stack() == [1]

    def test_ifelse_false(self):
        """Test ifelse operator with false condition."""
        interp = Interpreter()
        interp.run("false { 1 } { 2 } ifelse")
        assert interp.get_stack() == [2]

    def test_repeat(self):
        """Test repeat operator."""
        interp = Interpreter()
        interp.run("0 5 { 1 add } repeat")
        assert interp.get_stack() == [5]

    def test_for(self):
        """Test for operator."""
        interp = Interpreter()
        interp.run("0 1 1 5 { add } for")
        assert interp.get_stack() == [15]  # 0 + 1 + 2 + 3 + 4 + 5

    def test_loop_with_exit(self):
        """Test loop with exit."""
        interp = Interpreter()
        interp.run("0 { 1 add dup 5 eq { exit } if } loop")
        assert interp.get_stack() == [5]


class TestInterpreterDictionary:
    """Tests for dictionary operations."""

    def test_def(self):
        """Test def operator."""
        interp = Interpreter()
        interp.run("/x 42 def x")
        assert interp.get_stack() == [42]

    def test_def_procedure(self):
        """Test def with procedure."""
        interp = Interpreter()
        interp.run("/double { 2 mul } def 5 double")
        assert interp.get_stack() == [10]


class TestInterpreterArray:
    """Tests for array operations."""

    def test_array(self):
        """Test array operator."""
        interp = Interpreter()
        interp.run("3 array")
        stack = interp.get_stack()
        assert len(stack) == 1
        assert isinstance(stack[0], list)
        assert len(stack[0]) == 3

    def test_length(self):
        """Test length operator."""
        interp = Interpreter()
        interp.run("[1 2 3] length")
        assert interp.get_stack() == [3]

    def test_get(self):
        """Test get operator."""
        interp = Interpreter()
        interp.run("[10 20 30] 1 get")
        assert interp.get_stack() == [20]

    def test_put(self):
        """Test put operator."""
        interp = Interpreter()
        interp.run("[1 2 3] dup 1 99 put")
        stack = interp.get_stack()
        assert stack[0] == [1, 99, 3]


class TestInterpreterErrors:
    """Tests for error handling."""

    def test_stack_underflow(self):
        """Test stack underflow error."""
        interp = Interpreter()
        with pytest.raises(InterpreterError):
            interp.run("pop")

    def test_division_by_zero(self):
        """Test division by zero error."""
        interp = Interpreter()
        with pytest.raises(InterpreterError):
            interp.run("10 0 div")

    def test_undefined_name(self):
        """Test undefined name error."""
        interp = Interpreter()
        with pytest.raises(InterpreterError):
            interp.run("undefined_name")


class TestInterpreterIntegration:
    """Integration tests for the interpreter."""

    def test_factorial(self):
        """Test factorial calculation."""
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
        assert interp.get_stack() == [120]

    def test_fibonacci(self):
        """Test Fibonacci calculation."""
        interp = Interpreter()
        interp.run("""
            /fib {
                dup 2 lt
                { }
                { dup 1 sub fib exch 2 sub fib add }
                ifelse
            } def
            10 fib
        """)
        assert interp.get_stack() == [55]

    def test_complex_expression(self):
        """Test complex expression."""
        interp = Interpreter()
        interp.run("3 4 add 2 mul 5 sub")  # ((3 + 4) * 2) - 5 = 9
        assert interp.get_stack() == [9]
