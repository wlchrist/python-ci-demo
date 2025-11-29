"""Lexer/tokenizer for PostScript code."""

import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import Iterator


class TokenType(Enum):
    """Token types for PostScript lexer."""
    NUMBER = auto()
    NAME = auto()
    LITERAL_NAME = auto()
    STRING = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    EOF = auto()


@dataclass
class Token:
    """Represents a token in PostScript code."""
    type: TokenType
    value: object
    line: int = 0
    column: int = 0


class LexerError(Exception):
    """Exception raised for lexer errors."""
    pass


class Lexer:
    """Tokenizer for PostScript code."""

    def __init__(self, source: str):
        """Initialize the lexer with source code."""
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1

    def tokenize(self) -> Iterator[Token]:
        """Generate tokens from source code."""
        while self.pos < len(self.source):
            self._skip_whitespace_and_comments()
            if self.pos >= len(self.source):
                break

            char = self.source[self.pos]

            if char == '{':
                yield Token(TokenType.LBRACE, '{', self.line, self.column)
                self._advance()
            elif char == '}':
                yield Token(TokenType.RBRACE, '}', self.line, self.column)
                self._advance()
            elif char == '[':
                yield Token(TokenType.LBRACKET, '[', self.line, self.column)
                self._advance()
            elif char == ']':
                yield Token(TokenType.RBRACKET, ']', self.line, self.column)
                self._advance()
            elif char == '(':
                yield self._read_string()
            elif char == '/':
                yield self._read_literal_name()
            elif char == '-' or char == '+' or char == '.' or char.isdigit():
                yield self._read_number_or_name()
            else:
                yield self._read_name()

        yield Token(TokenType.EOF, None, self.line, self.column)

    def _advance(self) -> str:
        """Advance position and return current character."""
        if self.pos >= len(self.source):
            return ''
        char = self.source[self.pos]
        self.pos += 1
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char

    def _peek(self, offset: int = 0) -> str:
        """Peek at character at current position + offset."""
        pos = self.pos + offset
        if pos >= len(self.source):
            return ''
        return self.source[pos]

    def _skip_whitespace_and_comments(self) -> None:
        """Skip whitespace and comments."""
        while self.pos < len(self.source):
            char = self.source[self.pos]
            if char in ' \t\n\r':
                self._advance()
            elif char == '%':
                # Skip line comment
                while self.pos < len(self.source) and self.source[self.pos] != '\n':
                    self._advance()
            else:
                break

    def _read_string(self) -> Token:
        """Read a string literal (...)."""
        start_line = self.line
        start_col = self.column
        self._advance()  # Skip opening '('
        result = []
        depth = 1

        while self.pos < len(self.source) and depth > 0:
            char = self.source[self.pos]
            if char == '(':
                depth += 1
                result.append(char)
                self._advance()
            elif char == ')':
                depth -= 1
                if depth > 0:
                    result.append(char)
                self._advance()
            elif char == '\\':
                self._advance()  # Skip backslash
                if self.pos < len(self.source):
                    escape_char = self.source[self.pos]
                    if escape_char == 'n':
                        result.append('\n')
                    elif escape_char == 'r':
                        result.append('\r')
                    elif escape_char == 't':
                        result.append('\t')
                    elif escape_char == '\\':
                        result.append('\\')
                    elif escape_char == '(':
                        result.append('(')
                    elif escape_char == ')':
                        result.append(')')
                    else:
                        result.append(escape_char)
                    self._advance()
            else:
                result.append(char)
                self._advance()

        if depth != 0:
            raise LexerError(f"Unterminated string at line {start_line}, column {start_col}")

        return Token(TokenType.STRING, ''.join(result), start_line, start_col)

    def _read_literal_name(self) -> Token:
        """Read a literal name /name."""
        start_line = self.line
        start_col = self.column
        self._advance()  # Skip '/'
        name = self._read_name_chars()
        return Token(TokenType.LITERAL_NAME, name, start_line, start_col)

    def _read_name(self) -> Token:
        """Read an executable name."""
        start_line = self.line
        start_col = self.column
        name = self._read_name_chars()
        return Token(TokenType.NAME, name, start_line, start_col)

    def _read_name_chars(self) -> str:
        """Read name characters."""
        result = []
        delimiters = ' \t\n\r(){}[]<>/%'
        while self.pos < len(self.source) and self.source[self.pos] not in delimiters:
            result.append(self._advance())
        return ''.join(result)

    def _read_number_or_name(self) -> Token:
        """Read a number or a name that starts with a digit or sign."""
        start_line = self.line
        start_col = self.column
        start_pos = self.pos
        
        # Try to read as number
        result = []
        has_dot = False
        has_digit = False
        
        # Handle sign
        if self._peek() in '+-':
            result.append(self._advance())
        
        # Read digits and optional dot
        while self.pos < len(self.source):
            char = self._peek()
            if char.isdigit():
                has_digit = True
                result.append(self._advance())
            elif char == '.' and not has_dot:
                has_dot = True
                result.append(self._advance())
            else:
                break
        
        # Check if next char is a delimiter
        next_char = self._peek()
        delimiters = ' \t\n\r(){}[]<>/%'
        
        if has_digit and (next_char == '' or next_char in delimiters):
            # It's a number
            num_str = ''.join(result)
            try:
                if has_dot:
                    return Token(TokenType.NUMBER, float(num_str), start_line, start_col)
                else:
                    return Token(TokenType.NUMBER, int(num_str), start_line, start_col)
            except ValueError:
                pass
        
        # Not a number, reset and read as name
        self.pos = start_pos
        self.line = start_line
        self.column = start_col
        return self._read_name()
