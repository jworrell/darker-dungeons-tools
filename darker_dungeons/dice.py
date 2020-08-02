import threading
from dataclasses import dataclass
from random import randint

from sly import Lexer, Parser


@dataclass
class Operation:
    def eval(self, debug: bool = False) -> int:
        raise NotImplementedError


@dataclass
class Value(Operation):
    value: int

    def eval(self, debug: bool = False) -> int:
        rval = self.value

        if debug:
            print(f"Value({self.value}).eval() -> {rval}")

        return rval


@dataclass
class Add(Operation):
    left: Operation
    right: Operation

    def eval(self, debug: bool = False) -> int:
        left = self.left.eval(debug=debug)
        right = self.right.eval(debug=debug)
        rval = left + right

        if debug:
            print(f"Add({left}, {right}).eval() -> {rval}")

        return rval


@dataclass
class Sub(Operation):
    left: Operation
    right: Operation

    def eval(self, debug: bool = False) -> int:
        left = self.left.eval(debug=debug)
        right = self.right.eval(debug=debug)
        rval = left - right

        if debug:
            print(f"Sub({left}, {right}).eval() -> {rval}")

        return rval


@dataclass
class Mul(Operation):
    left: Operation
    right: Operation

    def eval(self, debug: bool = False) -> int:
        left = self.left.eval(debug=debug)
        right = self.right.eval(debug=debug)
        rval = left * right

        if debug:
            print(f"Mul({left}, {right}).eval() -> {rval}")

        return rval


@dataclass
class Roll(Operation):
    quantity: Operation
    sides: Operation

    def eval(self, debug: bool = False) -> int:
        sides = self.sides.eval(debug=debug)
        quantity = self.quantity.eval(debug=debug)
        rval = sum(randint(1, sides) for _ in range(quantity))

        if debug:
            print(f"Roll({quantity}, {sides}).eval() -> {rval}")

        return rval


class DiceLexer(Lexer):
    tokens = {
        NUM,
        DICE,
        MUL,
        ADD,
        SUB,
        LPAREN,
        RPAREN,
    }

    ignore = ' \t'

    DICE = r"[dD]"
    MUL = r"\*"
    ADD = r"\+"
    SUB = r"-"
    LPAREN = r"\("
    RPAREN = r"\)"

    @_(r"\d+")
    def NUM(self, t):
        t.value = int(t.value)
        return t


class DiceParser(Parser):
    # Get the token list from the lexer (required)
    tokens = DiceLexer.tokens

    @_("term")
    def expr(self, p):
        return p.term

    @_("term ADD term")
    def expr(self, p):
        return Add(p.term0, p.term1)

    @_("term SUB term")
    def expr(self, p):
        return Sub(p.term0, p.term1)

    @_("roll")
    def term(self, p):
        return p.roll

    @_("roll MUL roll")
    def term(self, p):
        # return p.roll0 * p.roll1
        return Mul(p.roll0, p.roll1)

    @_("factor DICE factor")
    def roll(self, p):
        return Roll(p.factor0, p.factor1)

    @_("factor")
    def roll(self, p):
        return p.factor

    @_("NUM")
    def factor(self, p):
        return Value(p.NUM)

    @_("LPAREN expr RPAREN")
    def factor(self, p):
        return p.expr


thread_locals = threading.local()


def make_parser():
    lexer = DiceLexer()
    parser = DiceParser()

    def parse(dice_expression):
        return parser.parse(lexer.tokenize(dice_expression))

    return parse


def parse_dice_expression(dice_expression: str) -> Operation:
    if (parse := getattr(thread_locals, "parse", None)) is None:
        parse = thread_locals.parse = make_parser()

    return parse(dice_expression)


def main():
    # op = parse_dice_expression("(1d6+1)d(1d6+1)*10")
    # print(op.eval(debug=True))
    op = parse_dice_expression("1d20-1")
    print(op.eval(debug=True))


if __name__ == "__main__":
    main()
