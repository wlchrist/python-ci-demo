"""Parser for PostScript code."""

from dataclasses import dataclass
from typing import List, Union
from .lexer import Lexer, Token, TokenType, LexerError


@dataclass
class Procedure:
    """Represents a PostScript procedure (code block)."""
    body: List[object]


@dataclass
class LiteralName:
    """Represents a literal name /name."""
    name: str


@dataclass
class ExecutableName:
    """Represents an executable name."""
    name: str


class ParserError(Exception):
    """Exception raised for parser errors."""
    pass


class Parser:
    """Parser for PostScript code."""

    def __init__(self, source: str):
        """Initialize the parser with source code."""
        self.lexer = Lexer(source)
        self.tokens = list(self.lexer.tokenize())
        self.pos = 0

    def parse(self) -> List[object]:
        """Parse the source and return a list of parsed objects."""
        result = []
        while not self._is_at_end():
            obj = self._parse_object()
            if obj is not None:
                result.append(obj)
        return result

    def _current(self) -> Token:
        """Get current token."""
        return self.tokens[self.pos]

    def _is_at_end(self) -> bool:
        """Check if at end of tokens."""
        return self._current().type == TokenType.EOF

    def _advance(self) -> Token:
        """Advance to next token and return current."""
        token = self._current()
        if not self._is_at_end():
            self.pos += 1
        return token

    def _parse_object(self) -> object:
        """Parse a single object."""
        token = self._current()

        if token.type == TokenType.NUMBER:
            self._advance()
            return token.value

        if token.type == TokenType.STRING:
            self._advance()
            return token.value

        if token.type == TokenType.LITERAL_NAME:
            self._advance()
            return LiteralName(token.value)

        if token.type == TokenType.NAME:
            self._advance()
            return ExecutableName(token.value)

        if token.type == TokenType.LBRACE:
            return self._parse_procedure()

        if token.type == TokenType.LBRACKET:
            return self._parse_array()

        if token.type == TokenType.RBRACE:
            raise ParserError(f"Unexpected '}}' at line {token.line}, column {token.column}")

        if token.type == TokenType.RBRACKET:
            raise ParserError(f"Unexpected ']' at line {token.line}, column {token.column}")

        if token.type == TokenType.EOF:
            return None

        raise ParserError(f"Unexpected token {token.type} at line {token.line}")

    def _parse_procedure(self) -> Procedure:
        """Parse a procedure {...}."""
        self._advance()  # Skip '{'
        body = []

        while not self._is_at_end() and self._current().type != TokenType.RBRACE:
            obj = self._parse_object()
            if obj is not None:
                body.append(obj)

        if self._is_at_end():
            raise ParserError("Unterminated procedure")

        self._advance()  # Skip '}'
        return Procedure(body)

    def _parse_array(self) -> list:
        """Parse an array [...]."""
        self._advance()  # Skip '['
        elements = []

        while not self._is_at_end() and self._current().type != TokenType.RBRACKET:
            obj = self._parse_object()
            if obj is not None:
                elements.append(obj)

        if self._is_at_end():
            raise ParserError("Unterminated array")

        self._advance()  # Skip ']'
        return elements
