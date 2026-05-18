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

    class TEKST(Token):
        pass


def je_akord(s):

    pattern = r'^[A-H](#|b)?m?$'

    return re.match(pattern, s) is not None

def je_znak(z):
    #Prihvačamo samo 'klasične' akorde.  kasnijim edicijama lako dodamo 'napredne' poput maj7, sus4...
    #Za amatere poput mene ovo je sasvim dovoljno
    if not z: return False
    return z.isalnum() or z in '#_'

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
        elif znak == '!':
            lex - "!"
            yield lex.token(T.TEKST)
        elif znak.isalpha():
            lex * je_znak

            sadržaj = lex.sadržaj

            if je_akord(sadržaj):
                yield lex.token(T.AKORD)

            else:
                yield lex.literal_ili(T.IME)

            lex.zanemari()

        else: 
            yield lex.literal(T)
        



### BKG
# start -> '' | start naredba
# naredba -> transponiraj | analiziraj | validacija | generate_pop | ispis
# analiziraj -> ANALYSE OTV lista_akorda ZATV
# transponiraj -> TRANSPOSE OTV lista_akorda ZAREZ pomak ZATV
# validacija -> VALIDATE OTV lista_akorda ZATV
# generate_pop -> GENERATE_POP OTV BROJ ZATV
# ispis -> ISPIS OTV pjesma ZATV
# lista_akorda -> UOTV elementi ZATV
# elementi ->AKORD ZAREZ elementi| AKORD
# pomak -> BROJ | PLUS BROJ| MINUS BROJ
# pjesma -> TEKST


class P(Parser):
    def start(p):
        naredbe = []

        while not p > KRAJ:
            naredbe.append(p.naredba())

        return Program(naredbe)

    def naredba(p):
        if p > T.TRANSPOSE:
            return p.transponiraj()

        elif p > T.ANALYSE:
            return p.analiziraj()

        elif p > T.VALIDATE:
            return p.validacija()

        elif p > T.GENERATE_POP:
            return p.generate_pop()

        elif p > T.ISPIS:
            return p.ispis()

        else:
            raise p.greška()


    def analiziraj(p):
        p >> T.ANALYSE
        p >> T.OTV

        akordi = p.lista_akorda()

        p >> T.ZATV

        return Analyse(akordi)

    def transponiraj(p):
        p >> T.TRANSPOSE
        p >> T.OTV
        
        akordi = p.lista_akorda()

        p >> T.ZAREZ

        pomak = p.pomak()

        p >> T.ZATV

        return Transpose(akordi, pomak)

    def validacija(p):
        p >> T.VALIDATE
        p >> T.OTV

        akordi = p.lista_akorda()

        p >> T.ZATV

        return Validate(akordi)

    def generate_pop(p):
        p >> T.GENERATE_POP
        p >> T.OTV
        broj = p >> T.BROJ

        p>>T.ZATV

        return GeneratePop(broj)

    def ispis(p):
        p >> T.ISPIS
        p >> T.OTV

        tekst = p>>T.TEKST

        p >> T.ZATV

        return Ispis(tekst)

    def lista_akorda(p):
        p >> T.UOTV

        akordi = [p >> T.AKORD]

        while p>= T.ZAREZ:
            akordi.append(p >> T.AKORD)

        p >> T.UZATV

        return ListaAkorda(akordi)


    def pomak(p):
        predznak = 1
        if p > T.MINUS:
            p.čitaj()
            predznak = -1
        
        if p > T.PLUS:
            p.čitaj()

        broj = p >> T.BROJ

        return Pomak(predznak, broj)
    


class Program(AST):
    naredbe: list

class Transpose(AST):
    akordi: list
    pomak: int


class Analyse(AST):
    akordi: list


class Validate(AST):
    akordi: list


class GeneratePop(AST):
    broj: Token


class Ispis(AST):
    tekst: Token


class ListaAkorda(AST):
    akordi: list


class Pomak(AST):
    predznak: Token
    broj: Token


    ## DEBUG TIME:
def testiranje(tekst):
    prikaz(P(tekst))

if __name__ == "__main__":

    testovi = [
        "analyse ([C, G, Am, F])",
        "transpose ([C, G, Am, F], +2)",
        "transpose ([C, G, Am, F], 2)",
        "generate_pop(8)",
        "ispis(!C Am F G!)",
        "C Am F G"
    ]

    for i, ulaz in enumerate(testovi):
        print("\n" + "=" * 50)
        print(f"TEST {i}: {ulaz}")
        print("-" * 50)

        try:
            testiranje(ulaz)
        except Exception as e:
            print("GREŠKA:", e)

            


