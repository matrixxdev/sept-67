#!/usr/bin/env python3
"""
███████╗███████╗██████╗ ████████╗
██╔════╝██╔════╝██╔══██╗╚══██╔══╝
███████╗█████╗  ██████╔╝   ██║
╚════██║██╔══╝  ██╔═══╝    ██║
███████║███████╗██║        ██║
╚══════╝╚══════╝╚═╝        ╚═╝

SEPT — The SEPTEM-67 Programming Language
Interpreter | Lexer | Parser | Runtime
"""

import sys
import os
import re
import math
from typing import Any, Optional

# ═══════════════════════════════════════════════════════
#  SEPTEM-67 CORE
# ═══════════════════════════════════════════════════════

DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzΩ·ΔΦΣ"
BASE = 67


def to_s67(n: int) -> str:
    """Convert integer to SEPTEM-67 string."""
    if n < 0:
        return "-" + to_s67(-n)
    if n == 0:
        return "0"
    result = ""
    while n > 0:
        result = DIGITS[n % BASE] + result
        n //= BASE
    return result


def from_s67(s: str) -> int:
    """Convert SEPTEM-67 string to integer."""
    if s.startswith("-"):
        return -from_s67(s[1:])
    result = 0
    for ch in s:
        idx = DIGITS.find(ch)
        if idx == -1:
            raise SeptError(f"Invalid SEPTEM-67 digit: '{ch}'")
        result = result * BASE + idx
    return result


def is_s67_literal(s: str) -> bool:
    """Check if string is a valid SEPTEM-67 literal (prefixed with §)."""
    return s.startswith("§") and all(c in DIGITS for c in s[1:])


# ═══════════════════════════════════════════════════════
#  ERRORS
# ═══════════════════════════════════════════════════════

class SeptError(Exception):
    def __init__(self, msg, line=None):
        self.msg = msg
        self.line = line
        super().__init__(msg)

    def __str__(self):
        prefix = f"[Line {self.line}] " if self.line else ""
        return f"\n  ⬡ SEPT ERROR {prefix}→ {self.msg}\n"


# ═══════════════════════════════════════════════════════
#  TOKENS
# ═══════════════════════════════════════════════════════

TT = {
    # Literals
    "S67":      "S67",        # §1A  (SEPTEM-67 number literal)
    "DEC":      "DEC",        # decimal number
    "STRING":   "STRING",     # "hello"
    "BOOL":     "BOOL",       # Ω·Δ (true) / Ω·Φ (false)
    "IDENT":    "IDENT",      # variable name
    # Operators
    "PLUS":     "PLUS",       # Σ+
    "MINUS":    "MINUS",      # Σ-
    "MUL":      "MUL",        # Σ*
    "DIV":      "DIV",        # Σ/
    "MOD":      "MOD",        # Σ%
    "POW":      "POW",        # Σ^
    # Comparison
    "EQ":       "EQ",         # ==
    "NEQ":      "NEQ",        # !=
    "LT":       "LT",         # <
    "GT":       "GT",         # >
    "LTE":      "LTE",        # <=
    "GTE":      "GTE",        # >=
    # Logic
    "AND":      "AND",        # ΩΔ
    "OR":       "OR",         # ΩΦ
    "NOT":      "NOT",        # ΩΣ
    # Assignment
    "ASSIGN":   "ASSIGN",     # :=
    # Delimiters
    "LPAREN":   "LPAREN",     # (
    "RPAREN":   "RPAREN",     # )
    "LBRACE":   "LBRACE",     # {
    "RBRACE":   "RBRACE",     # }
    "LBRACKET": "LBRACKET",   # [
    "RBRACKET": "RBRACKET",   # ]
    "COMMA":    "COMMA",      # ,
    "COLON":    "COLON",      # :
    "DOT":      "DOT",        # .
    # Keywords
    "LET":      "LET",        # ΔΩ  (variable declaration)
    "PRINT":    "PRINT",      # Φ   (print)
    "PRINTRAW": "PRINTRAW",   # ΦΔ  (print as s67)
    "IF":       "IF",         # Δif
    "ELSE":     "ELSE",       # Δelse
    "LOOP":     "LOOP",       # Ω67 (loop N times)
    "WHILE":    "WHILE",      # ΩΔΩ (while loop)
    "FUNC":     "FUNC",       # ΣΩ  (function def)
    "RETURN":   "RETURN",     # ΣΣ  (return)
    "BREAK":    "BREAK",      # ΣΔ  (break)
    "IN":       "IN",         # ΣΦ  (for-in keyword)
    "RANGE":    "RANGE",      # range()
    "IMPORT":   "IMPORT",     # ΩΩ  (import)
    "TRUE":     "TRUE",       # Ω·Δ
    "FALSE":    "FALSE",      # Ω·Φ
    "NULL":     "NULL",       # Ω·Σ
    "EOF":      "EOF",
    "NEWLINE":  "NEWLINE",
}

KEYWORDS = {
    "ΔΩ":   TT["LET"],
    "Φ":    TT["PRINT"],
    "ΦΔ":   TT["PRINTRAW"],
    "Δif":  TT["IF"],
    "Δelse":TT["ELSE"],
    "Ω67":  TT["LOOP"],
    "ΩΔΩ":  TT["WHILE"],
    "ΣΩ":   TT["FUNC"],
    "ΣΣ":   TT["RETURN"],
    "ΣΔ":   TT["BREAK"],
    "ΣΦ":   TT["IN"],
    "ΩΩ":   TT["IMPORT"],
    "Ω·Δ":  TT["TRUE"],
    "Ω·Φ":  TT["FALSE"],
    "Ω·Σ":  TT["NULL"],
    # Operators
    "ΩΔ":   TT["AND"],
    "ΩΦ":   TT["OR"],
    "ΩΣ":   TT["NOT"],
    # Built-ins
    "range": TT["RANGE"],
}


class Token:
    def __init__(self, type_, value, line):
        self.type = type_
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type}, {self.value!r})"


# ═══════════════════════════════════════════════════════
#  LEXER
# ═══════════════════════════════════════════════════════

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.tokens = []

    def error(self, msg):
        raise SeptError(msg, self.line)

    def peek(self, offset=0):
        i = self.pos + offset
        return self.source[i] if i < len(self.source) else None

    def advance(self):
        ch = self.source[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
        return ch

    def match(self, expected):
        if self.pos < len(self.source) and self.source[self.pos] == expected:
            self.pos += 1
            return True
        return False

    def skip_comment(self):
        # Comment: ΩΩΩ ... until end of line
        while self.pos < len(self.source) and self.source[self.pos] != "\n":
            self.pos += 1

    def read_string(self):
        result = ""
        while self.pos < len(self.source):
            ch = self.advance()
            if ch == '"':
                return result
            if ch == "\\" and self.pos < len(self.source):
                esc = self.advance()
                result += {"n": "\n", "t": "\t", "\\": "\\", '"': '"'}.get(esc, esc)
            else:
                result += ch
        self.error("Unterminated string")

    def read_s67_literal(self):
        # §[SEPTEM-67 digits]
        result = ""
        while self.pos < len(self.source) and self.source[self.pos] in DIGITS:
            result += self.advance()
        if not result:
            self.error("Empty SEPTEM-67 literal after §")
        return result

    def read_number(self, first):
        result = first
        while self.pos < len(self.source) and (self.source[self.pos].isdigit() or self.source[self.pos] == "."):
            result += self.advance()
        return result

    def read_keyword_or_ident(self):
        """Read identifiers and special Unicode keywords."""
        result = ""
        special_chars = set("ΔΩΦΣΩΩΔΦΣΩΔΩΔifelse67ΔΩΦΣrange")
        # Read Unicode or ASCII word characters
        while self.pos < len(self.source):
            ch = self.source[self.pos]
            if ch.isalnum() or ch == "_" or (ord(ch) > 127 and ch not in '§"{}()[],:=<>!+\\-*/%^&|.·\n\t '):
                result += ch
                self.pos += 1
            else:
                break
        return result

    def tokenize(self):
        while self.pos < len(self.source):
            ch = self.source[self.pos]

            # Whitespace (not newline)
            if ch in " \t\r":
                self.pos += 1
                continue

            # Newline
            if ch == "\n":
                self.pos += 1
                # Only add NEWLINE if last token is meaningful
                if self.tokens and self.tokens[-1].type not in (TT["NEWLINE"], TT["LBRACE"]):
                    self.tokens.append(Token(TT["NEWLINE"], "\n", self.line))
                continue

            # Comment: ΩΩΩ
            if self.source[self.pos:self.pos+3] == "ΩΩΩ":
                self.pos += 3  # each Ω is 2 bytes in UTF-8 but Python handles it
                self.skip_comment()
                continue

            # SEPTEM-67 literal: §...
            if ch == "§":
                self.pos += 1
                val = self.read_s67_literal()
                self.tokens.append(Token(TT["S67"], val, self.line))
                continue

            # String
            if ch == '"':
                self.pos += 1
                val = self.read_string()
                self.tokens.append(Token(TT["STRING"], val, self.line))
                continue

            # Number (decimal)
            if ch.isdigit():
                val = self.read_number(self.advance())
                num = float(val) if "." in val else int(val)
                self.tokens.append(Token(TT["DEC"], num, self.line))
                continue

            # Two-char operators
            two = self.source[self.pos:self.pos+2]
            if two == ":=":
                self.pos += 2
                self.tokens.append(Token(TT["ASSIGN"], ":=", self.line))
                continue
            if two == "==":
                self.pos += 2
                self.tokens.append(Token(TT["EQ"], "==", self.line))
                continue
            if two == "!=":
                self.pos += 2
                self.tokens.append(Token(TT["NEQ"], "!=", self.line))
                continue
            if two == "<=":
                self.pos += 2
                self.tokens.append(Token(TT["LTE"], "<=", self.line))
                continue
            if two == ">=":
                self.pos += 2
                self.tokens.append(Token(TT["GTE"], ">=", self.line))
                continue

            # Single-char operators
            simple = {
                "+": TT["PLUS"], "-": TT["MINUS"], "*": TT["MUL"],
                "/": TT["DIV"],  "%": TT["MOD"],   "^": TT["POW"],
                "<": TT["LT"],   ">": TT["GT"],
                "(": TT["LPAREN"], ")": TT["RPAREN"],
                "{": TT["LBRACE"], "}": TT["RBRACE"],
                "[": TT["LBRACKET"], "]": TT["RBRACKET"],
                ",": TT["COMMA"], ":": TT["COLON"], ".": TT["DOT"],
            }
            if ch in simple:
                self.tokens.append(Token(simple[ch], ch, self.line))
                self.pos += 1
                continue

            # Unicode keywords and identifiers
            if ch.isalpha() or ch == "_" or ord(ch) > 127:
                word = self.read_keyword_or_ident()
                tok_type = KEYWORDS.get(word, TT["IDENT"])
                self.tokens.append(Token(tok_type, word, self.line))
                continue

            self.error(f"Unknown character: {ch!r}")

        self.tokens.append(Token(TT["EOF"], None, self.line))
        return self.tokens


# ═══════════════════════════════════════════════════════
#  AST NODES
# ═══════════════════════════════════════════════════════

class Node:
    pass

class NumberNode(Node):
    def __init__(self, value, is_s67=False):
        self.value = value
        self.is_s67 = is_s67  # if True, value is already int from s67

class StringNode(Node):
    def __init__(self, value):
        self.value = value

class BoolNode(Node):
    def __init__(self, value):
        self.value = value

class NullNode(Node):
    pass

class IdentNode(Node):
    def __init__(self, name):
        self.name = name

class BinOpNode(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class UnaryOpNode(Node):
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand

class AssignNode(Node):
    def __init__(self, name, value):
        self.name = name
        self.value = value

class LetNode(Node):
    def __init__(self, name, value):
        self.name = name
        self.value = value

class PrintNode(Node):
    def __init__(self, expr, raw=False):
        self.expr = expr
        self.raw = raw  # if True, print as S67

class IfNode(Node):
    def __init__(self, condition, then_body, else_body=None):
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body

class LoopNode(Node):
    def __init__(self, count, body, var=None):
        self.count = count
        self.body = body
        self.var = var  # optional loop variable name

class WhileNode(Node):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class FuncDefNode(Node):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

class FuncCallNode(Node):
    def __init__(self, name, args):
        self.name = name
        self.args = args

class ReturnNode(Node):
    def __init__(self, value):
        self.value = value

class BreakNode(Node):
    pass

class BlockNode(Node):
    def __init__(self, statements):
        self.statements = statements

class ListNode(Node):
    def __init__(self, elements):
        self.elements = elements

class IndexNode(Node):
    def __init__(self, obj, index):
        self.obj = obj
        self.index = index

class RangeNode(Node):
    def __init__(self, args):
        self.args = args


# ═══════════════════════════════════════════════════════
#  PARSER
# ═══════════════════════════════════════════════════════

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        return self.tokens[self.pos]

    def peek(self, offset=1):
        i = self.pos + offset
        return self.tokens[i] if i < len(self.tokens) else self.tokens[-1]

    def advance(self):
        tok = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return tok

    def expect(self, type_):
        tok = self.current()
        if tok.type != type_:
            raise SeptError(f"Expected {type_}, got {tok.type} ({tok.value!r})", tok.line)
        return self.advance()

    def skip_newlines(self):
        while self.current().type == TT["NEWLINE"]:
            self.advance()

    def parse(self):
        stmts = []
        self.skip_newlines()
        while self.current().type != TT["EOF"]:
            stmts.append(self.parse_statement())
            while self.current().type in (TT["NEWLINE"], ):
                self.advance()
        return BlockNode(stmts)

    def parse_block(self):
        self.expect(TT["LBRACE"])
        self.skip_newlines()
        stmts = []
        while self.current().type not in (TT["RBRACE"], TT["EOF"]):
            stmts.append(self.parse_statement())
            while self.current().type == TT["NEWLINE"]:
                self.advance()
        self.expect(TT["RBRACE"])
        return BlockNode(stmts)

    def parse_statement(self):
        tok = self.current()

        if tok.type == TT["LET"]:
            return self.parse_let()
        if tok.type == TT["PRINT"]:
            return self.parse_print(raw=False)
        if tok.type == TT["PRINTRAW"]:
            return self.parse_print(raw=True)
        if tok.type == TT["IF"]:
            return self.parse_if()
        if tok.type == TT["LOOP"]:
            return self.parse_loop()
        if tok.type == TT["WHILE"]:
            return self.parse_while()
        if tok.type == TT["FUNC"]:
            return self.parse_func()
        if tok.type == TT["RETURN"]:
            self.advance()
            val = self.parse_expr()
            return ReturnNode(val)
        if tok.type == TT["BREAK"]:
            self.advance()
            return BreakNode()
        if tok.type == TT["IDENT"] and self.peek().type == TT["ASSIGN"]:
            return self.parse_assign()
        if tok.type == TT["NEWLINE"]:
            self.advance()
            return BlockNode([])

        # Expression statement (e.g. function call)
        return self.parse_expr()

    def parse_let(self):
        self.expect(TT["LET"])
        name = self.expect(TT["IDENT"]).value
        self.expect(TT["ASSIGN"])
        value = self.parse_expr()
        return LetNode(name, value)

    def parse_assign(self):
        name = self.advance().value
        self.expect(TT["ASSIGN"])
        value = self.parse_expr()
        return AssignNode(name, value)

    def parse_print(self, raw):
        self.advance()
        expr = self.parse_expr()
        return PrintNode(expr, raw)

    def parse_if(self):
        self.expect(TT["IF"])
        condition = self.parse_expr()
        self.skip_newlines()
        then_body = self.parse_block()
        else_body = None
        self.skip_newlines()
        if self.current().type == TT["ELSE"]:
            self.advance()
            self.skip_newlines()
            if self.current().type == TT["IF"]:
                else_body = self.parse_if()
            else:
                else_body = self.parse_block()
        return IfNode(condition, then_body, else_body)

    def parse_loop(self):
        self.expect(TT["LOOP"])
        # Ω67 count [ΣΦ varname] { body }
        count = self.parse_expr()
        var = None
        if self.current().type == TT["IN"]:
            self.advance()
            var = self.expect(TT["IDENT"]).value
        self.skip_newlines()
        body = self.parse_block()
        return LoopNode(count, body, var)

    def parse_while(self):
        self.expect(TT["WHILE"])
        condition = self.parse_expr()
        self.skip_newlines()
        body = self.parse_block()
        return WhileNode(condition, body)

    def parse_func(self):
        self.expect(TT["FUNC"])
        name = self.expect(TT["IDENT"]).value
        self.expect(TT["LPAREN"])
        params = []
        while self.current().type != TT["RPAREN"]:
            params.append(self.expect(TT["IDENT"]).value)
            if self.current().type == TT["COMMA"]:
                self.advance()
        self.expect(TT["RPAREN"])
        self.skip_newlines()
        body = self.parse_block()
        return FuncDefNode(name, params, body)

    def parse_expr(self):
        return self.parse_or()

    def parse_or(self):
        left = self.parse_and()
        while self.current().type == TT["OR"]:
            op = self.advance().value
            right = self.parse_and()
            left = BinOpNode(left, "OR", right)
        return left

    def parse_and(self):
        left = self.parse_comparison()
        while self.current().type == TT["AND"]:
            op = self.advance().value
            right = self.parse_comparison()
            left = BinOpNode(left, "AND", right)
        return left

    def parse_comparison(self):
        left = self.parse_addition()
        comp_ops = {TT["EQ"]: "==", TT["NEQ"]: "!=", TT["LT"]: "<",
                    TT["GT"]: ">", TT["LTE"]: "<=", TT["GTE"]: ">="}
        while self.current().type in comp_ops:
            op = comp_ops[self.advance().type]
            right = self.parse_addition()
            left = BinOpNode(left, op, right)
        return left

    def parse_addition(self):
        left = self.parse_multiplication()
        while self.current().type in (TT["PLUS"], TT["MINUS"]):
            op = self.advance().value
            right = self.parse_multiplication()
            left = BinOpNode(left, op, right)
        return left

    def parse_multiplication(self):
        left = self.parse_power()
        while self.current().type in (TT["MUL"], TT["DIV"], TT["MOD"]):
            op = self.advance().value
            right = self.parse_power()
            left = BinOpNode(left, op, right)
        return left

    def parse_power(self):
        left = self.parse_unary()
        if self.current().type == TT["POW"]:
            self.advance()
            right = self.parse_power()
            return BinOpNode(left, "^", right)
        return left

    def parse_unary(self):
        if self.current().type == TT["MINUS"]:
            self.advance()
            return UnaryOpNode("-", self.parse_unary())
        if self.current().type == TT["NOT"]:
            self.advance()
            return UnaryOpNode("NOT", self.parse_unary())
        return self.parse_postfix()

    def parse_postfix(self):
        node = self.parse_primary()
        while True:
            if self.current().type == TT["LBRACKET"]:
                self.advance()
                idx = self.parse_expr()
                self.expect(TT["RBRACKET"])
                node = IndexNode(node, idx)
            elif self.current().type == TT["LPAREN"] and isinstance(node, IdentNode):
                # Function call
                name = node.name
                self.advance()
                args = []
                while self.current().type != TT["RPAREN"]:
                    args.append(self.parse_expr())
                    if self.current().type == TT["COMMA"]:
                        self.advance()
                self.expect(TT["RPAREN"])
                node = FuncCallNode(name, args)
            else:
                break
        return node

    def parse_primary(self):
        tok = self.current()

        if tok.type == TT["S67"]:
            self.advance()
            return NumberNode(from_s67(tok.value), is_s67=True)

        if tok.type == TT["DEC"]:
            self.advance()
            return NumberNode(tok.value)

        if tok.type == TT["STRING"]:
            self.advance()
            return StringNode(tok.value)

        if tok.type == TT["TRUE"]:
            self.advance()
            return BoolNode(True)

        if tok.type == TT["FALSE"]:
            self.advance()
            return BoolNode(False)

        if tok.type == TT["NULL"]:
            self.advance()
            return NullNode()

        if tok.type == TT["RANGE"]:
            self.advance()
            self.expect(TT["LPAREN"])
            args = []
            while self.current().type != TT["RPAREN"]:
                args.append(self.parse_expr())
                if self.current().type == TT["COMMA"]:
                    self.advance()
            self.expect(TT["RPAREN"])
            return RangeNode(args)

        if tok.type == TT["IDENT"]:
            self.advance()
            return IdentNode(tok.value)

        if tok.type == TT["LPAREN"]:
            self.advance()
            expr = self.parse_expr()
            self.expect(TT["RPAREN"])
            return expr

        if tok.type == TT["LBRACKET"]:
            self.advance()
            elements = []
            while self.current().type != TT["RBRACKET"]:
                elements.append(self.parse_expr())
                if self.current().type == TT["COMMA"]:
                    self.advance()
            self.expect(TT["RBRACKET"])
            return ListNode(elements)

        raise SeptError(f"Unexpected token: {tok.type} ({tok.value!r})", tok.line)


# ═══════════════════════════════════════════════════════
#  RUNTIME
# ═══════════════════════════════════════════════════════

class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value

class BreakSignal(Exception):
    pass

class SeptFunction:
    def __init__(self, name, params, body, env):
        self.name = name
        self.params = params
        self.body = body
        self.env = env  # closure

    def __repr__(self):
        return f"<func {self.name}({', '.join(self.params)})>"


class Environment:
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise SeptError(f"Undefined variable: '{name}'")

    def set(self, name, value):
        self.vars[name] = value

    def assign(self, name, value):
        if name in self.vars:
            self.vars[name] = value
        elif self.parent:
            self.parent.assign(name, value)
        else:
            raise SeptError(f"Undefined variable: '{name}' (use ΔΩ to declare)")


class Interpreter:
    def __init__(self):
        self.global_env = Environment()
        self._setup_builtins()

    def _setup_builtins(self):
        g = self.global_env
        # Built-in functions
        g.set("s67", lambda args: to_s67(int(self._num(args[0]))))
        g.set("dec", lambda args: float(from_s67(str(args[0]))) if isinstance(args[0], str) else args[0])
        g.set("len", lambda args: float(len(args[0])))
        g.set("str", lambda args: self._to_str(args[0]))
        g.set("num", lambda args: float(args[0]) if not isinstance(args[0], SeptFunction) else 0)
        g.set("sqrt", lambda args: math.sqrt(self._num(args[0])))
        g.set("abs",  lambda args: abs(self._num(args[0])))
        g.set("floor",lambda args: float(math.floor(self._num(args[0]))))
        g.set("ceil", lambda args: float(math.ceil(self._num(args[0]))))
        g.set("pow",  lambda args: self._num(args[0]) ** self._num(args[1]))
        g.set("max",  lambda args: max(self._num(a) for a in args))
        g.set("min",  lambda args: min(self._num(a) for a in args))
        g.set("type", lambda args: type(args[0]).__name__)
        g.set("append", lambda args: args[0].append(args[1]) or args[0])
        g.set("pop",  lambda args: args[0].pop() if args else None)
        g.set("input", lambda args: input(args[0] if args else ""))

    def _num(self, v):
        if isinstance(v, bool):
            return 1.0 if v else 0.0
        if isinstance(v, (int, float)):
            return float(v)
        try:
            return float(v)
        except:
            raise SeptError(f"Cannot convert '{v}' to number")

    def _to_str(self, v):
        if v is None:
            return "Ω·Σ"
        if isinstance(v, bool):
            return "Ω·Δ" if v else "Ω·Φ"
        if isinstance(v, float) and v == int(v):
            return str(int(v))
        if isinstance(v, list):
            return "[" + ", ".join(self._to_str(x) for x in v) + "]"
        return str(v)

    def _is_truthy(self, v):
        if v is None:
            return False
        if isinstance(v, bool):
            return v
        if isinstance(v, (int, float)):
            return v != 0
        if isinstance(v, str):
            return len(v) > 0
        if isinstance(v, list):
            return len(v) > 0
        return True

    def execute(self, node, env):
        if isinstance(node, BlockNode):
            result = None
            for stmt in node.statements:
                result = self.execute(stmt, env)
            return result

        if isinstance(node, NumberNode):
            return float(node.value)

        if isinstance(node, StringNode):
            return node.value

        if isinstance(node, BoolNode):
            return node.value

        if isinstance(node, NullNode):
            return None

        if isinstance(node, IdentNode):
            val = env.get(node.name)
            if callable(val):
                return val  # built-in function
            return val

        if isinstance(node, ListNode):
            return [self.execute(e, env) for e in node.elements]

        if isinstance(node, RangeNode):
            args = [int(self._num(self.execute(a, env))) for a in node.args]
            if len(args) == 1:
                return list(range(args[0]))
            elif len(args) == 2:
                return list(range(args[0], args[1]))
            elif len(args) == 3:
                return list(range(args[0], args[1], args[2]))
            raise SeptError("range() takes 1-3 arguments")

        if isinstance(node, LetNode):
            val = self.execute(node.value, env)
            env.set(node.name, val)
            return val

        if isinstance(node, AssignNode):
            val = self.execute(node.value, env)
            env.assign(node.name, val)
            return val

        if isinstance(node, PrintNode):
            val = self.execute(node.expr, env)
            if node.raw:
                # Print as S67
                if isinstance(val, (int, float)):
                    print(to_s67(int(val)))
                else:
                    print(self._to_str(val))
            else:
                print(self._to_str(val))
            return val

        if isinstance(node, BinOpNode):
            return self._binop(node, env)

        if isinstance(node, UnaryOpNode):
            val = self.execute(node.operand, env)
            if node.op == "-":
                return -self._num(val)
            if node.op == "NOT":
                return not self._is_truthy(val)
            raise SeptError(f"Unknown unary op: {node.op}")

        if isinstance(node, IfNode):
            cond = self.execute(node.condition, env)
            if self._is_truthy(cond):
                return self.execute(node.then_body, Environment(env))
            elif node.else_body:
                return self.execute(node.else_body, Environment(env))
            return None

        if isinstance(node, LoopNode):
            count = self.execute(node.count, env)
            if isinstance(count, list):
                items = count
            else:
                items = range(int(self._num(count)))
            loop_env = Environment(env)
            try:
                for i in items:
                    if node.var:
                        loop_env.set(node.var, float(i))
                    try:
                        self.execute(node.body, loop_env)
                    except BreakSignal:
                        break
            except ReturnSignal:
                raise
            return None

        if isinstance(node, WhileNode):
            try:
                while True:
                    cond = self.execute(node.condition, env)
                    if not self._is_truthy(cond):
                        break
                    try:
                        self.execute(node.body, Environment(env))
                    except BreakSignal:
                        break
            except ReturnSignal:
                raise
            return None

        if isinstance(node, FuncDefNode):
            fn = SeptFunction(node.name, node.params, node.body, env)
            env.set(node.name, fn)
            return fn

        if isinstance(node, FuncCallNode):
            fn = env.get(node.name)
            args = [self.execute(a, env) for a in node.args]
            if callable(fn):
                return fn(args)
            if isinstance(fn, SeptFunction):
                fn_env = Environment(fn.env)
                for param, arg in zip(fn.params, args):
                    fn_env.set(param, arg)
                try:
                    self.execute(fn.body, fn_env)
                except ReturnSignal as r:
                    return r.value
                return None
            raise SeptError(f"'{node.name}' is not a function")

        if isinstance(node, ReturnNode):
            val = self.execute(node.value, env)
            raise ReturnSignal(val)

        if isinstance(node, BreakNode):
            raise BreakSignal()

        if isinstance(node, IndexNode):
            obj = self.execute(node.obj, env)
            idx = int(self._num(self.execute(node.index, env)))
            if isinstance(obj, (list, str)):
                return float(obj[idx]) if isinstance(obj[idx], int) else obj[idx]
            raise SeptError(f"Cannot index type {type(obj).__name__}")

        return None

    def _binop(self, node, env):
        op = node.op

        # Short-circuit
        if op == "AND":
            l = self.execute(node.left, env)
            return l if not self._is_truthy(l) else self.execute(node.right, env)
        if op == "OR":
            l = self.execute(node.left, env)
            return l if self._is_truthy(l) else self.execute(node.right, env)

        left = self.execute(node.left, env)
        right = self.execute(node.right, env)

        if op == "+":
            if isinstance(left, str) or isinstance(right, str):
                return self._to_str(left) + self._to_str(right)
            if isinstance(left, list) and isinstance(right, list):
                return left + right
            return self._num(left) + self._num(right)
        if op == "-": return self._num(left) - self._num(right)
        if op == "*":
            if isinstance(left, str) and isinstance(right, (int, float)):
                return left * int(self._num(right))
            return self._num(left) * self._num(right)
        if op == "/":
            r = self._num(right)
            if r == 0: raise SeptError("Division by zero (even in base 67!)")
            return self._num(left) / r
        if op == "%": return self._num(left) % self._num(right)
        if op == "^": return self._num(left) ** self._num(right)
        if op == "==": return left == right
        if op == "!=": return left != right
        if op == "<":  return self._num(left) < self._num(right)
        if op == ">":  return self._num(left) > self._num(right)
        if op == "<=": return self._num(left) <= self._num(right)
        if op == ">=": return self._num(left) >= self._num(right)
        raise SeptError(f"Unknown operator: {op}")


# ═══════════════════════════════════════════════════════
#  REPL + RUNNER
# ═══════════════════════════════════════════════════════

BANNER = """
\033[38;5;214m ███████╗███████╗██████╗ ████████╗\033[0m
\033[38;5;214m ██╔════╝██╔════╝██╔══██╗╚══██╔══╝\033[0m
\033[38;5;220m ███████╗█████╗  ██████╔╝   ██║\033[0m
\033[38;5;226m ╚════██║██╔══╝  ██╔═══╝    ██║\033[0m
\033[38;5;154m ███████║███████╗██║        ██║\033[0m
\033[38;5;82m ╚══════╝╚══════╝╚═╝        ╚═╝\033[0m
\033[36m The SEPTEM-67 Programming Language  v1.0\033[0m
\033[90m Type 'exit' to quit | .help for commands\033[0m
"""


def run_source(source: str, interpreter: Interpreter = None, filename="<input>"):
    if interpreter is None:
        interpreter = Interpreter()
    try:
        tokens = Lexer(source).tokenize()
        ast = Parser(tokens).parse()
        interpreter.execute(ast, interpreter.global_env)
    except SeptError as e:
        print(f"\033[31m{e}\033[0m", file=sys.stderr)
    except KeyboardInterrupt:
        print("\n\033[33m[Interrupted]\033[0m")
    return interpreter


def repl():
    print(BANNER)
    interp = Interpreter()
    import readline  # noqa: F401 (enables arrow keys)
    while True:
        try:
            line = input("\033[36m⬡ sept>\033[0m ")
        except (EOFError, KeyboardInterrupt):
            print("\n\033[90mΩ·Σ — Goodbye!\033[0m")
            break
        if not line.strip():
            continue
        if line.strip() == "exit":
            print("\033[90mΩ·Σ — Goodbye!\033[0m")
            break
        if line.strip() == ".help":
            print_help()
            continue
        if line.strip() == ".symbols":
            print_symbols()
            continue
        run_source(line, interp)


def print_help():
    help_text = """
\033[36m═══ SEPT Language Reference ═══\033[0m

\033[33mVariables:\033[0m
  ΔΩ name := value        Declare variable
  name := value           Reassign variable

\033[33mLiterals:\033[0m
  §1A                     SEPTEM-67 number (§ prefix)
  42                      Decimal number
  "hello"                 String
  Ω·Δ / Ω·Φ              true / false
  Ω·Σ                     null

\033[33mOutput:\033[0m
  Φ expr                  Print (decimal)
  ΦΔ expr                 Print as SEPTEM-67

\033[33mControl Flow:\033[0m
  Δif cond { }            If statement
  Δif cond { } Δelse { }  If-else
  Ω67 N ΣΦ i { }         Loop N times (i = index)
  ΩΔΩ cond { }           While loop

\033[33mFunctions:\033[0m
  ΣΩ name(a, b) { }      Define function
  ΣΣ value               Return value
  ΣΔ                     Break from loop

\033[33mOperators:\033[0m
  + - * / % ^            Arithmetic
  == != < > <= >=        Comparison
  ΩΔ ΩΦ ΩΣ               and / or / not

\033[33mBuilt-ins:\033[0m
  s67(n)    Convert to SEPTEM-67 string
  dec(s)    Convert S67 string to decimal
  len(x)    Length of string/list
  sqrt(n)   Square root
  abs(n)    Absolute value
  input(p)  Read user input
  range(n)  Generate list 0..n-1

\033[90m  ΩΩΩ This is a comment\033[0m
"""
    print(help_text)


def print_symbols():
    print("\n\033[36m═══ SEPTEM-67 Symbol Table ═══\033[0m")
    for i, ch in enumerate(DIGITS):
        end = "\n" if (i + 1) % 10 == 0 else "  "
        print(f"\033[33m{ch}\033[0m=\033[90m{i:2d}\033[0m", end=end)
    print()


def main():
    if len(sys.argv) == 1:
        repl()
    elif len(sys.argv) == 2:
        filename = sys.argv[1]
        if not os.path.exists(filename):
            print(f"\033[31mFile not found: {filename}\033[0m")
            sys.exit(1)
        with open(filename, encoding="utf-8") as f:
            source = f.read()
        run_source(source, filename=filename)
    else:
        print("Usage: sept [file.sept]")
        sys.exit(1)


if __name__ == "__main__":
    main()
