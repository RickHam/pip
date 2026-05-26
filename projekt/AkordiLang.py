from vepar import *
import re

#Klasična definica ljestvica nota i progresija. Problematični su E->F, i B->C bez E#, B# 
#Pa sa standardnom logikom prebacivanja bi se pošteno namučili
NOTE = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
ROMAN = ['I', 'bII', 'II', 'bIII', 'III', 'IV', 'bV', 'V', 'bVI', 'VI', 'bVII', 'VII']

PROGRESSIONS = [
        ["C", "G", "Am", "F"],
        ["C", "Am", "F", "G"],
        ["Am", "F", "C", "G"],
        ["C", "G", "F", "F"],
    ]

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
        def vrijednost(self): return int(self.sadržaj)

        
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
    #Prihvačamo samo 'klasične' akorde.  kasnijim edicijama možemo dodati 'napredne' poput maj7, sus4...
    #Za amatere poput mene ovo je sasvim dovoljno
    if not z: return False
    return z.isalnum() or z in '#_'


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
                #Mjenjamo H u B po standardu
                if sadržaj.startswith('H'):
                    sadržaj = 'B' + sadržaj[1:]
                    lex.sadržaj = sadržaj
                    print("Promjenjen H akordu u B po Njemačkom standardu\n")
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
# transponiraj -> TRANSPOSE OTV izraz ZAREZ pomak ZATV
# validacija -> VALIDATE OTV izraz ZATV
# generate_pop -> GENERATE_POP OTV BROJ ZATV
# izraz -> lista_akorda | generate_pop | transpose | akord
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

        izraz = p.izraz()

        p >> T.ZATV

        return Analyse(izraz)

    def transponiraj(p):
        p >> T.TRANSPOSE
        p >> T.OTV
        
        akordi = p.izraz()

        p >> T.ZAREZ

        pomak = p.pomak()

        p >> T.ZATV

        return Transpose(akordi, pomak)
    
    def izraz(p):
        if p > T.UOTV:
            return p.lista_akorda()
        
        if p > T.GENERATE_POP:
            return p.generate_pop()

        elif p > T.TRANSPOSE:
            return p.transponiraj()

        elif p > T.AKORD:
            return ListaAkorda([p >> T.AKORD])
        
        else:
            raise p.greška()

    def validacija(p):
        p >> T.VALIDATE
        p >> T.OTV

        akordi = p.izraz()

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


#AST TIME! 


class Program(AST):
    naredbe: 'naredba*'
    def izvrši(program):
        rt.memorija = Memorija()

        rezultat = None
        for naredba in program.naredbe: 
            rezultat = naredba.izvrši()

        return rezultat

class Transpose(AST):
    izraz: 'AST'
    pomak: 'int'

    def izvrši(self):
        lista = self.izraz.izvrši()

        pravi_pomak = self.pomak.predznak * self.pomak.broj.vrijednost()

        rezultat = []

        for akord in lista.akordi:
            s = akord.sadržaj
            minor = s.endswith('m')

            if(minor):
                korijen = s[:-1]
            else:
                korijen = s
            
            idx = NOTE.index(korijen)
            novi_idx = (idx + pravi_pomak) % len(NOTE)

            novi_akord = NOTE[novi_idx]

            if minor:
                novi_akord += 'm'

            rezultat.append(novi_akord)

        return ListaAkorda([Token(T.AKORD,x) for x in rezultat])   
                

class Analyse(AST):
    izraz: 'izraz'

    def izvrši(self):
        akordi = self.izraz.izvrši()

        result = []
        for akord in akordi:
            s= akord.sadržaj

            minor = s.endswith('m')
            root = s[:-1] if minor else s

            idx = NOTE.index(root)
            result.append(ROMAN[idx].lower() if minor else ROMAN[idx])
        
        print(result)
        return result
        


class Validate(AST):
    akordi: list


class GeneratePop(AST):
    broj: Token

    def izvrši(self):
        n = self.broj.vrijednost()
        pattern = PROGRESSIONS[n % len(PROGRESSIONS)]

        return ListaAkorda([Token(T.AKORD,x) for x in pattern])


class Ispis(AST):
    tekst: Token


class ListaAkorda(AST):
    akordi: list

    def izvrši(self):
        return self.akordi


class Pomak(AST):
    predznak: Token
    broj: Token


    ## DEBUG TIME:

def testiraj(tekst):
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
            testiraj(ulaz)
        except Exception as e:
            print("GREŠKA:", e)

            


