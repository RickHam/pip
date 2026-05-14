from vepar import *
import re

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
        def vrijednost(self, mem, unutar): return int(self.sadržaj)

        
    class AKORD(Token):
        pass

    class IME(Token):
        pass


def je_akord(s):

    pattern = r'^[A-H](#|b)?m?$'

    return re.match(pattern, s) is not None

def je_znak(z):
    #Prihvačamo samo 'klasične' akorde.  kasnijim edicijama lako dodamo napredne poput maj7, sus4...
    #Za amatere poput mene ovo je sasvim dovoljno
    if not z: return False
    return z.isalnum() or z in "#_b"

keywords = {'transpose',
            'analyse',
            'validate',
            'generate_pop',
            'ispis'
            }

@lexer
def ac(lex):
    for znak in lex:
        if znak.isspace(): lex.zanemari()
        elif znak.isdecimal():
            lex.prirodni_broj(znak)
            yield lex.token(T.BROJ)
        elif znak.isalpha() or znak in '#_':
            lex * je_znak

            sadržaj = lex.sadržaj

            if sadržaj in keywords:
                yield lex.literal(T)

            elif je_akord(sadržaj):
                yield lex.token(T.AKORD)

            else:
                yield lex.token(T.IME)

            lex.zanemari()

        else: 
            yield lex.literal(T)
        




if __name__ == "__main__":

    testovi = [
        "C Am F G",
        "transpose C + 2",
        "analyse [C, G, Am, F]",
        "validate C = G",
        "generate_pop C Am F G",
        "C#m Bb Am G#",
        "ispis C + Am",
        "C invalid_token 123 Am",
    ]
    i = 0
    for ulaz in testovi:
        print("test broj:  ", i)
        print("\n" + "="*40)
        print("ULAZ:", ulaz)
        print("-"*40)

        try:
            tokens = list(ac(ulaz))

            for t in tokens:
                print(f"{t.__class__.__name__:<10} | {t.sadržaj}")

        except Exception as e:
            print("GREŠKA:", e)