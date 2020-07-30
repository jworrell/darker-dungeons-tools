from random import randint

from sly import Lexer, Parser


class DiceLexer(Lexer):
    tokens = {
        NUM,
        DICE,
        MUL,
        ADD,
        LPAREN,
        RPAREN,
    }

    ignore = ' \t'

    DICE = r"[dD]"
    MUL = r"\*"
    ADD = r"\+"
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
        return p.term0 + p.term1

    @_("roll")
    def term(self, p):
        return p.roll

    @_("roll MUL roll")
    def term(self, p):
        return p.roll0 * p.roll1

    @_("factor DICE factor")
    def roll(self, p):
        return sum(randint(1, p.factor1) for _ in range(p.factor0))

    @_("factor")
    def roll(self, p):
        return p.factor

    @_("NUM")
    def factor(self, p):
        return p.NUM

    @_("LPAREN expr RPAREN")
    def factor(self, p):
        return p.expr


def main():
    data = '10d6'
    lexer = DiceLexer()
    parser = DiceParser()

    result = parser.parse(lexer.tokenize(data))
    print(resuslt)


if __name__ == "__main__":
    main()
