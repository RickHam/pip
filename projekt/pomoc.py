from vepar import *

class T(TipoviTokena):
    OTV, ZATV, UOTV, UZATV = '()[]'
    ZAREZ = ','
    JEDNAKO, PLUS, MINUS = '=+-'

    TRANSPOSE = 'transpose'
    ANALYSE = 'analyse'
    VALIDATE = 'validate'
    GENERATE_POP = 'generate_pop'
    ISPIS = 'ispis'

    class BROJ(Token):
        def vrijednost(t):
            return int(t.sadržaj)
        
    class AKORD(Token):
        pass

    class IME(Token):
        pass



@lexer
def akordilang(lex):
    for znak in lex:

        # whitespace
        if znak.isspace():
            lex.zanemari()

        # brojevi
        elif znak.isdecimal():
            lex.prirodni_broj(znak)
            yield lex.token(T.BROJ)

        # riječi / akordi / funkcije
        elif znak.isalpha():

            lex * (lambda z: z.isalnum() or z in '#m_')

            sadržaj = lex.sadržaj

            # funkcije / keywordsi
            if sadržaj in {
                'transpose',
                'analyse',
                'validate',
                'generate_pop',
                'ispis'
            }:
                yield lex.literal(T)

            # akordi
            elif je_akord(sadržaj):
                yield lex.token(T.AKORD)

            # identifikatori
            else:
                yield lex.token(T.IME)

        # operatori i simboli
        else:
            yield lex.literal(T)