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

    @_("factor")
    def term(self, p):
        return p.factor

    @_("factor MUL factor")
    def term(self, p):
        return p.factor0 * p.factor1

    @_("NUM")
    def factor(self, p):
        return p.NUM

    @_("roll")
    def factor(self, p):
        return p.roll

    @_("LPAREN expr RPAREN")
    def factor(self, p):
        return p.expr

    @_("NUM DICE NUM")
    def roll(self, p):
        return sum(randint(1, p.NUM1) for _ in range(p.NUM0))


def main():
    data = '(3d6)d6'
    lexer = DiceLexer()
    # for tok in lexer.tokenize(data):
    #     print('type=%r, value=%r' % (tok.type, tok.value))

    parser = DiceParser()

    result = parser.parse(lexer.tokenize(data))
    print(result)


if __name__ == "__main__":
    main()
