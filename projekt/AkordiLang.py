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
        elif znak == '"':
            lex.pročitaj_do('"', uključivo=False)
            yield lex.token(T.TEKST)
            lex.čitaj()   # pojedi završni "
            lex.zanemari()
        elif znak.isalpha():
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
    pjesma: Token


class ListaAkorda(AST):
    akordi: list


class Pomak(AST):
    predznak: Token
    broj: Token

class P(Parser):
    def start(p):
        ...

    def naredba(p):
        ...

    def analiziraj(p):
        ...

    def transponiraj(p):
        ...

    def validacija(p):
        ...

    def generate_pop(p):
        ...

    def ispis(p):
        ...

    def lista_akorda(p):
        ...

    def elementi(p):
        ...

    def pomak(p):
        ...

    def pjesma(p):
        ...


