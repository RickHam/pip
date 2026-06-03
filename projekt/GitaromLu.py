from vepar import *
import re
import json, os


# Patrik želi naučiti svirati gitaru. 
# Zna osnovne akorde, ali ne zna muzičku teoriju ni koje pjesme imaju koje akorde.
# Kao kolega koji voli tipkati po računalu želi neki programski jezik
# koji će mu pomoći da na tekstove pjesama upiše akorde za gitaru.
# Također kako je on amater, neki akordi su mu teški za uhvatiti
# pa ponekad želi transponirati akorde za lakše hvatove.
# Kako u slobodno vrijeme želi napisati pokoju pjesmu i odsvirati na gitari
# želi mogučnost generiranja progresija koje zvuče "dobro"
# te uopće provjeriti je li neka dana progresija zvuči "dobro" 
# On dobro zna odsvirati pjesme ako su mu dani akordi
# Za to mu treba baza podataka u koju će spremati pjesmu s akordima

# Ovaj programski jezik je napravljen da pomogne korisnicima poput Patrika.
# Dolazi s funkcijama transpose, analyse, validate, generate_pop koji
# upravo zadovoljavaju njegove potrebe. 



# Podržane naredbe:
#
# transpose(progresija, pomak)
#     Transponira sve akorde za zadani broj polustepena.
#
# analyse(progresija)
#     Prikazuje progresiju u obliku rimskih brojeva.
#
# validate(progresija)
#     Provjerava pripadaju li svi akordi istoj harmoniji.
#
# generate_pop(n)
#     Generira unaprijed definiranu popularnu progresiju.
#
# dodaj_pjesmu(izvođač, naslov, tekst)
#     Sprema pjesmu u JSON bazu.
#
# ucitaj_pjesmu(izvođač, naslov)
#     Učitava pjesmu iz JSON baze.
#
# izbrisi_pjesmu(izvođač, naslov)
#     Briše pjesmu iz JSON baze.
#
# izvuci_akorde(pjesma)
#     Vraća listu svih akorda pronađenih u pjesmi.
#
# zamjeni_akorde(pjesma, progresija)
#     Zamjenjuje postojeće akorde novima.
#
# dodaj_progresiju(progresija)
#     Dodaje novu akordnu progresiju u bazu (progressions.json).
#
# izbrisi_progresiju(indeks)
#     Briše progresiju na zadanoj poziciji iz baze.
#
# ucitaj_progresiju()
#     Učitava sve progresije iz baze u memoriju programa.
#
# generate_pop(n)
#     Generira pop progresiju na temelju unaprijed definiranih uzoraka.

# Klasična definica ljestvica nota i progresija. 
# Problematični su E->F, i B->C jer ne postoje E#, B# 
# Pa sa standardnom logikom prebacivanja bi se pošteno namučili
NOTE = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
ROMAN = ['I', 'bII', 'II', 'bIII', 'III', 'IV', 'bV', 'V', 'bVI', 'VI', 'bVII', 'VII']


class T(TipoviTokena):
    OTV, ZATV, UOTV, UZATV = '()[]'
    ZAREZ = ','
    JEDNAKO, PLUS, MINUS = '=+-'

    TRANSPOSE = 'transpose'
    ANALYSE = 'analyse'
    VALIDATE = 'validate'
    GENERATE_POP = 'generate_pop'
    ISPIS = 'ispis'
    
    DODAJ_PJESMU = 'dodaj_pjesmu'
    IZBRISI_PJESMU = 'izbrisi_pjesmu'
    UCITAJ_PJESMU = 'ucitaj_pjesmu'

    DODAJ_PROGRESIJU = 'dodaj_progresiju'
    IZBRISI_PROGRESIJU = 'izbrisi_progresiju'
    UCITAJ_PROGRESIJU = 'ucitaj_progresiju'

    IZVUCI_AKORDE = 'izvuci_akorde'
    ZAMJENI_AKORDE = 'zamjeni_akorde'

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
            lex.pročitaj_do("!", više_redova = True)
            yield lex.token(T.TEKST)
        elif znak.isalpha():
            lex * je_znak

            sadržaj = lex.sadržaj

            if je_akord(sadržaj):
                #Mjenjamo H u B po standardu
                if sadržaj.startswith('H'):
                    sadržaj = 'B' + sadržaj[1:]
                    print("Zamjenjen H akord s B po Njemačkom standardu\n")
                yield Token(T.AKORD, sadržaj)

            else:
                yield lex.literal_ili(T.IME)

            lex.zanemari()

        else: 
            yield lex.literal(T)
        



### BKG
# start -> '' | start naredba
# naredba -> pridruživanje | transponiraj | analiziraj | validacija | generate_pop | ispis | izraz|
#            dodaj_progresiju | izbrisi_progresiju| ucitaj_progresiju
#            dodaj_pjesmu| ucitaj_pjesmu| izbrisi_pjesmu | zamjeni_akorde
#            izvuci_akorde
# pridruživanje -> IME JEDNAKO izraz
# analiziraj -> ANALYSE OTV lista_akorda ZATV
# transponiraj -> TRANSPOSE OTV izraz ZAREZ pomak ZATV
# validacija -> VALIDATE OTV izraz ZATV
# generate_pop -> GENERATE_POP OTV BROJ ZATV
# izraz -> lista_akorda | IME | generate_pop | transponiraj | izvuci_akorde | akord | ucitaj_pjesmu
# ispis -> ISPIS OTV pjesma ZATV
# dodaj_pjesmu ->DODAJ_PJESMU OTV IME ZAREZ IME ZAREZ TEKST ZATV
# izbrisi_pjesmu -> IZBRISI_PJESMU OTV IME ZAREZ IME ZATV
# ucitaj_pjesmu -> UCITAJ_PJESMU OTV IME ZAREZ IME ZATV
# dodaj_progresiju -> DODAJ_PROGRESIJU OTV izraz ZATV
# izbrisi_progresiju -> IZBRISI_PROGRESIJU OTV BROJ ZATV
# ucitaj_progresiju -> UCITAJ_PROGRESIJU OTV ZATV
# izvuci_akorde -> IZVUCI_AKORDE OTV pjesma ZATV
# zamjeni_akorde -> ZAMJENI_AKORDE OTV pjesma ZAREZ izraz ZATV
# lista_akorda -> UOTV elementi ZATV
# elementi ->AKORD (ZAREZ AKORD)*
# pomak -> BROJ | PLUS BROJ| MINUS BROJ
# pjesma -> TEKST | IME 


class P(Parser):
    def start(p):
        naredbe = []

        while not p > KRAJ:
            naredbe.append(p.naredba())

        return Program(naredbe)

    def naredba(p):
        if p > T.IME:
            return p.pridruživanje()
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
        
        elif p > T.DODAJ_PJESMU:
            return p.dodaj_pjesmu()
        
        elif p > T.IZBRISI_PJESMU:
            return p.izbrisi_pjesmu()

        elif p > T.UCITAJ_PJESMU:
            return p.ucitaj_pjesmu()

        elif p > T.DODAJ_PROGRESIJU:
            return p.dodaj_progresiju()

        elif p > T.IZBRISI_PROGRESIJU:
            return p.izbrisi_progresiju()

        elif p > T.UCITAJ_PROGRESIJU:
            return p.ucitaj_progresiju()
        elif p > T.IZVUCI_AKORDE:
            return p.izvuci_akorde()
        elif p > T.IZBRISI_PJESMU:
            return p.izbrisi_pjesmu()
        elif p > T.ZAMJENI_AKORDE:
            return p.zamjeni_akorde()

        else:
            raise p.greška()

    def pridruživanje(p):
        ime = p >> T.IME

        p >> T.JEDNAKO

        izraz = p.izraz()

        return Pridruživanje(ime, izraz)

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
        
        elif p > T.GENERATE_POP:
            return p.generate_pop()

        elif p > T.TRANSPOSE:
            return p.transponiraj()
        
        elif p > T.IZVUCI_AKORDE:
            return p.izvuci_akorde()
        
        elif p > T.UCITAJ_PJESMU:
            return p.ucitaj_pjesmu()

        elif p > T.ZAMJENI_AKORDE:
            return p.zamijeni_akorde()

        elif p > T.AKORD:
            return ListaAkorda([p >> T.AKORD])
        
        elif p> T.IME:
            return Dohvati(p>>T.IME)
                
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

        if p > T.TEKST:
            argument = Tekst(p >> T.TEKST)
        elif p > T.IME:
            argument = Dohvati(p >> T.IME)
        else:
            raise p.greška()

        p >> T.ZATV

        return Ispis(argument)
    
    def izvuci_akorde(p):
        p >> T.IZVUCI_AKORDE
        p >> T.OTV

        if p > T.TEKST:
            argument = Tekst(p >> T.TEKST)
        elif p > T.IME:
            argument = Dohvati(p >> T.IME)
        else:
            raise p.greška()

        p >> T.ZATV

        return IzvuciAkorde(argument)



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
    
    def dodaj_pjesmu(p):
        p >> T.DODAJ_PJESMU
        p >> T.OTV

        artist = p >> T.IME
        p >> T.ZAREZ

        title = p >> T.IME
        p >> T.ZAREZ

        text = p.izraz()

        p >> T.ZATV

        return DodajPjesmu(text, title, artist)
    
    def izbrisi_pjesmu(p):
        p >> T.IZBRISI_PJESMU
        p >> T.OTV

        title = p >> T.IME
        p >> T.ZAREZ
        artist = p >> T.IME

        p >> T.ZATV

        return IzbrisiPjesmu(title, artist)
    
    def zamijeni_akorde(p):
        p >> T.ZAMJENI_AKORDE
        p >> T.OTV

        tekst = p.izraz()
        p >> T.ZAREZ
        akordi = p.izraz()

        p >> T.ZATV

        return ZamijeniAkorde(tekst, akordi)
    
    def ucitaj_pjesmu(p):
        p >> T.UCITAJ_PJESMU
        p >> T.OTV

        artist = p >> T.IME
        p >> T.ZAREZ
        title = p >> T.IME

        p >> T.ZATV

        return UcitajPjesmu(artist, title)
    
    def dodaj_progresiju(p):
        p >> T.DODAJ_PROGRESIJU
        p >> T.OTV

        prog = p.izraz()

        p >> T.ZATV

        return DodajProgresiju(prog)
    
    def izbrisi_progresiju(p):
        p >> T.IZBRISI_PROGRESIJU
        p >> T.OTV

        idx = p >> T.BROJ

        p >> T.ZATV

        return IzbrisiProgresiju(idx)
    
    def ucitaj_progresiju(p):
        p >> T.UCITAJ_PROGRESIJU
        p >> T.OTV
        p >> T.ZATV

        return UcitajProgressiju()



#Pomočne funkcije za AST
def odredi_skalu(korijen):
    novi_korijen = korijen
    ima_m = ''
    intervali = []
    if korijen.endswith('m'):
        novi_korijen = korijen[:-1]
        intervali = [2, 1, 2, 2, 1, 2, 2] #mol skala
    else:
        intervali = [2, 2, 1, 2, 2, 2, 1] #dur skala
    idx = NOTE.index(novi_korijen)
    

    skala = [novi_korijen]

    for korak in intervali:
        idx = (idx + korak) % 12
        skala.append(NOTE[idx] + ima_m)

    return skala[:-1]


def harmonija(nota):
    scale = odredi_skalu(nota)
    mol = nota.endswith('m')
    result = []
    
    for i, note in enumerate(scale[:7]):
        if mol == False:
            if i in [1,2,5]:
                result.append(note + 'm')
            else:
                result.append(note)

        else:
            if i in [0, 3, 4]:
                result.append(note)
            else:
                result.append(note + 'm')


    return result


def izvuci_akorde_iz_pjesme(tekst):
    result = []
    chords = re.findall(r'\[([A-H](?:#|b)?m?)\]' , tekst)
    if chords:

        for chord in chords:
            result.append(Token(T.AKORD, chord))
    
    print("Izvućeni akordi su ", result)
    return result



### AST
#
# Program: naredbe:[naredba]
#
# naredba:
#     Pridruživanje: ime:IME izraz:izraz
#     Transpose: izraz:izraz pomak:pomak
#     Analyse: izraz:izraz
#     Validate: izraz:izraz
#     GeneratePop: broj:BROJ
#     Ispis: izraz:izraz
#     DodajPjesmu: artist:IME | TEKST title:IME | TEKST text: IME | TEKST
#     UcitajPjesmu: artist:IME | TEKST title:IME | TEKST
#     IzbrisiPjesmu: artist:IME | TEKST title:IME | TEKST
#     IzvuciAkorde: izraz:izraz
#     ZamijeniAkorde: tekst:izraz akordi:izraz
#     DodajProgresiju: progresija:izraz
#     IzbrisiProgresiju: index:BROJ
#     UcitajProgresiju: (nema argumenata)
#
# izraz:
#     ListaAkorda: akordi:[AKORD]
#     Dohvati: ime:IME
#     Akord: AKORD
#
# pomak:
#     Pomak: predznak:(PLUS|MINUS|EPSILON) broj:BROJ
#
# vrijednosti:
#     AKORD: string (npr. "C", "Am", "G#")
#     BROJ: int
#     IME: string
#     TEKST: string
#
# napomena:
#     Svi AST čvorovi implementiraju metodu izvrši()
#     koja vraća:
#         - listu AKORD tokena
#         - string (pjesma)
#         - broj (int)
#         - ili None (npr. ispis)




rt.memorija = Memorija() #Odma se inicijalizira, da testovi ne resetiraju memoriju
class Dohvati(AST):
    ime: 'IME'

    def izvrši(self):

        return rt.memorija[self.ime.sadržaj]
    
    
class Program(AST):
    naredbe: 'naredba*'
    def izvrši(program):
        #rt.memorija = Memorija()

        rezultat = None
        for naredba in program.naredbe: 
            rezultat = naredba.izvrši()

        return rezultat

class Transpose(AST):
    izraz: 'Lista_akorda | izraz'
    pomak: 'pomak'

    def izvrši(self):
        lista = self.izraz.izvrši()

        pravi_pomak = self.pomak.izvrši()

        rezultat = []

        for akord in lista:
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
        print("rezultat Transposea: ", rezultat)
        return [Token(T.AKORD,x) for x in rezultat]
                
class Pridruživanje(AST):
    ime: 'IME'
    izraz: 'IZRAZ'

    def izvrši(self):

        vrijednost = self.izraz.izvrši()

        rt.memorija[self.ime.sadržaj] = vrijednost

        print(f"Spremljeno u varijablu '{self.ime.sadržaj}'")

        return vrijednost
    
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
        
        print("Rezultat analize: ", result)
        return result
        


class Validate(AST):
    izraz: 'izraz'

    def izvrši(self):
        akordi = self.izraz.izvrši()
        print("Provjera validnosti progresije: ", akordi)
        root = akordi[0].sadržaj

        progresija = harmonija(root)
        for akord in akordi:
            if akord.sadržaj not in progresija:
                print("Invalidna progresija")
                return False
        print("Validna progresija")
        return True


class GeneratePop(AST):
    broj: 'BROJ'

    def izvrši(self):
        n = self.broj.vrijednost()
        pattern = PROGRESSIONS[n % len(PROGRESSIONS)]
        print("Generirana progresija: ", pattern)
        result = [Token(T.AKORD,x) for x in pattern]
        return result


class Ispis(AST):
    tekst: 'IME | TEKST'

    def izvrši(self):

        tekst = self.tekst.izvrši()

        linije = tekst.split('\n')

        for linija in linije:

            akordi_red = ''
            tekst_red = ''

            i = 0

            while i < len(linija):

                if linija[i] == '[':

                    kraj = linija.index(']', i)

                    akord = linija[i+1:kraj]

                    akordi_red += akord

                    # poravnanje
                    tekst_red += ' ' * len(akord)

                    i = kraj + 1

                else:
                    akordi_red += ' '
                    tekst_red += linija[i]
                    i += 1

            print(akordi_red)
            print(tekst_red)
            print()

class ListaAkorda(AST):
    akordi: 'Lista_Akorda'

    def izvrši(self):
        return self.akordi

class Pomak(AST):
    predznak: '(PLUS|MINUS)?'
    broj: 'BROJ'

    def izvrši(self):
        return self.predznak * self.broj.vrijednost()

class DodajPjesmu(AST):
    text: 'IME | TEKST'
    title: 'IME | TEKST'
    artist: 'IME | TEKST'
    def izvrši(self):
        tekst = self.text.izvrši()
        add_song(tekst, self.title.sadržaj, self.artist.sadržaj,"songs.json",True)
        return None

class UcitajPjesmu(AST):
    artist: 'IME | TEKST'
    title: 'IME | TEKST'

    def izvrši(self):
        song = find_song(self.artist.sadržaj, self.title.sadržaj)

        if song is None:
            print("Pjesma nije pronađena")

        return song

class IzbrisiPjesmu(AST):
    title: 'IME | TEKST'
    artist: 'IME | TEKST'

    def izvrši(self):
        remove_song(
            self.title.sadržaj,
            self.artist.sadržaj
        )

class Tekst(AST):
    token: 'TEKST'

    def izvrši(self):
        return self.token.sadržaj

class UcitajProgressiju(AST):
    def izvrši(self):
        updateProgressions()

class DodajProgresiju(AST):
    progresija: 'Lista_Akorda'

    def izvrši(self):
        prog = [akord.sadržaj for akord in self.progresija.izvrši()]
        add_progression(prog)
        print("Dodana progresija")

class IzbrisiProgresiju(AST):
    index: 'BROJ'

    def izvrši(self):
        idx = self.index.vrijednost()
        remove_progression(idx)
        print(f"Obrisana progresija {idx}")


class IzvuciAkorde(AST):
    izraz: 'IME | TEKST'

    def izvrši(self):

        tekst = self.izraz.izvrši()


        return izvuci_akorde_iz_pjesme(tekst)


class Akord(AST):
    token: ...

    def izvrši(self):
        return self.token.sadržaj
    

class ZamijeniAkorde(AST):
    tekst: 'IME | TEKST'
    akordi: 'izraz'

    def izvrši(self):
        tekst = self.tekst.izvrši()
        akordi = self.akordi.izvrši()

        akordi = [akord.sadržaj for akord in akordi]

        return ubaci_akorde_u_pjesmu(tekst, akordi)



#Funkcije za JSON i runtime.

PROGRESSIONS = [[]] 

def load_progressions(filename="progressions.json"):
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data["progressions"]

def ubaci_akorde_u_pjesmu(tekst, novi_akordi):
    pattern = r'\[([A-H](?:#|b)?m?)\]'

    it = iter(novi_akordi)

    def replacer(match):
        try:
            return f"[{next(it)}]"
        except StopIteration:
            return match.group(0)

    return re.sub(pattern, replacer, tekst)    

def save_progressions(progressions, filename="progressions.json"):
    data = {
        "progressions": progressions
    }

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    
    updateProgressions()

def add_progression(progression, filename="progressions.json"):
    progressions = load_progressions()

    if progression in progressions:
        print("Progresija već postoji. Nije dodana")
        return

    progressions.append(progression)

    save_progressions(progressions)

    updateProgressions()

def remove_progression(index, filename="progressions.json"):
    progressions = load_progressions(filename)

    if 0 <= index < len(progressions):
        del progressions[index]
        save_progressions(progressions, filename)
    updateProgressions()

        

def updateProgressions():
    global PROGRESSIONS
    PROGRESSIONS = load_progressions(filename="progressions.json")


PROGRESSIONS = load_progressions(filename="progressions.json") 

def load_songs(filename = "songs.json"):
    if not os.path.exists(filename):
        return []
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["songs"]

def save_songs(songs, filename = "songs.json"):
    data = {
        "songs" : songs
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f,indent=4)

def add_song(text, title= "Unknown", artist="Unknown", filename="songs.json", Replace = False):
    songs = load_songs(filename)

    song = {
        "artist": artist,
        "title": title,
        "text": text
    }

    for s in songs:
        if s["title"].lower() == title.lower() and s["artist"].lower() == artist.lower():
            print("Pjesma već postoji.")

            if Replace:
                s["text"] = text
                save_songs(songs,filename)
                print("Pjesma je zamjenjena")
            
            return

    songs.append(song)
    print("Pjesma je dodana")
    save_songs(songs, filename)

def remove_song(title, artist, filename="songs.json"):
    songs = load_songs(filename)

    novi_popis = []

    obrisana = False

    for song in songs:
        if (song["title"].lower() == title.lower()
            and song["artist"].lower() == artist.lower()
        ):
            obrisana = True
            continue

        novi_popis.append(song)

    save_songs(novi_popis, filename)

    if obrisana:
        print(f"Obrisana pjesma: {artist} - {title}")
    else:
        print("Pjesma nije pronađena.")

def find_song(artist, title, filename="songs.json"):
    songs = load_songs(filename)

    for song in songs:
        if song["artist"].lower() == artist.lower() and song["title"].lower() == title.lower():
            return song["text"]
    
    return None

    


def iz(tekst):
    P(tekst).izvrši()

def testiraj(tekst):
    prikaz(P(tekst))

if __name__ == "__main__":

    testovi = [
        "analyse (transpose([C, G, Am, F], 2))",
        "transpose ([C, G, Am, F], +2)",
        "transpose ([C, G, Am, F], 2)",
        "generate_pop(8)",
        "ispis(!C Am F G!)",
        "verse = [C,G,Am,F]",
        "chorus = transpose(verse, 2)",
        "analyse(transpose(chorus,2))",
        "analyse(transpose(generate_pop(3),2))",
        "validate(verse)",
        "chorus = transpose(verse, 2)",
        "pop = generate_pop(1)",
        "validate(pop)",

        #Izvlačenje i mjenjanje pjesme iz baze
        "song = ucitaj_pjesmu(Bajaga, Tisina)",
        "verse = izvuci_akorde(song)",
        "ispis(song)",
        "trans = transpose(verse, -2)",
        "analyse(trans)",
        "nova_pjesma = zamjeni_akorde(song, trans)",
        "dodaj_pjesmu(Bajaga, Tisina, nova_pjesma)",


        "song = ucitaj_pjesmu(Bajaga, Tisina)",
        "verse = izvuci_akorde(song)",
        "ispis(song)",
        "trans = transpose(verse, +2)",
        "analyse(trans)",
        "nova_pjesma = zamjeni_akorde(song, trans)",
        "dodaj_pjesmu(Bajaga, Tisina, nova_pjesma)"
    ]
    

    for i, ulaz in enumerate(testovi):
        print("\n" + "=" * 50)
        print(f"TEST {i}: {ulaz}")
        print("-" * 50)

        try:
            testiraj(ulaz)
            iz(ulaz)
        except Exception as e:
            print("GREŠKA:", e)
    

            

#OFC najpopularnija pjesma za poćet učiti gitaru
bajaga_tisina = """[Am]Mrak se skupio u kap, [C]rano jutro kao [G]slap ulazi u sobu
[Am]Da l' si ikada pitala [C]tamne senke zidova [G]ujutro gde odu
[Am]Oči su ti sklopljene,[C] usne su ti umorne [G]Ne ljubi me njima
[Am]Nisu čvorci pevali [C]dok je iznad krovova [G]svirala tišina


[Am]Hajde, Bože, budi drug[C] pa okreni jedan krug[G] unazad planetu
[Am]Noć je kratko trajala[C] a nama je trebala,[G] ovolika najduža na svetu
[Am]U mom oku samo hlad, [C]u mom srcu samo stud, [G]inje i prašina
[Am]Nisu čvorci pevali[C] dok je iznad krovova [G]svirala tišina

[Am]U cik zore zviždi voz, [C]njime odlazim u OZ [G]Neću da se vratim
[Am]Što god tebi napišem [C]pocepam i obrišem [G]Al' ti moraš znati
[Am]Nisi se probudila,[C] zato nisi videla, [G]igrale su sene
[Am]Nek' te dobri duhovi[C] i kraljevski orlovi [G]čuvaju od mene"""