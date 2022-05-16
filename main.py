import enum
import random
from tkinter import RIDGE
from pkg_resources import yield_lines
import haravasto
import time


tila = {
    "kentta": [],
    "aloitusaika": 0,
    "esitettava_kentta": [],
    "miinat": 0,
    "lippujen_tilanne": [],
    "lopputulos": [],
    "ruutuja_jaljella": [],
    "loppu": False,
    "vuorot": 0,
    "avaamattomat": 0,
    "leveys": 0,
    "korkeus": 0,
    "miinojen_lkm": 0,
    "pelin_kesto": 0,
    "paivamaara_aika": []
}


def kasittele_hiiri(x, y, nappi, muokkausnapit):
    """
    Tätä funktiota kutsutaan kun käyttäjä klikkaa sovellusikkunaa hiirellä.
    """
    x = int(x / 40)
    y = int(y / 40)
    if nappi == haravasto.HIIRI_OIKEA:
        asettaja(x, y)
    elif nappi == haravasto.HIIRI_VASEN:
        ruudun_avaaja(x, y)


def piirra_kentta():
    """
    Käsittelijäfunktio, joka piirtää kaksiulotteisena listana kuvatun miinakentän
    ruudut näkyviin peli-ikkunaan. Funktiota kutsutaan aina kun pelimoottori pyytää
    ruudun näkymän päivitystä.
    """
    haravasto.tyhjaa_ikkuna()
    haravasto.piirra_tausta()
    haravasto.aloita_ruutujen_piirto()
    for x in range(len(tila["esitettava_kentta"])):
        for y in range(len(tila["esitettava_kentta"][0])):
        
            haravasto.lisaa_piirrettava_ruutu(
                tila["esitettava_kentta"][x][y], x * 40, y * 40)
    haravasto.piirra_ruudut()


def miinoita(miina_kentta, miinojen_lkm):
    """
    Asettaa kentälle N kpl miinoja satunnaisiin paikkoihin.
    """
    tila["miinat"] = miinojen_lkm
    jaljella = []
    for j, rivi in enumerate(miina_kentta):
        for i in range(len(rivi)):
            jaljella.append((i, j))
    for x in range(miinojen_lkm):
        tyhjat = random.choice(jaljella)
        i, j = tyhjat
        jaljella.remove(tyhjat)
        miina_kentta[j][i] = "x"
    
    
def laske_naapurit(y_coord, x_coord):
    """
    Laskee ympärillä olevien miinojen lukumäärän
    """
    rivit = len(tila["kentta"][0])
    sarakkeet = len(tila["kentta"])
    naapurit = []
    for i in range(y_coord-1, y_coord+2):
        for j in range(x_coord-1, x_coord+2):
            if i < rivit and j < sarakkeet:
                if i >= 0 and j >= 0:
                    naapurit.append((j, i))
    return naapurit


def tulvataytto(y, x, tarkastetut=[]):
    """
    Merkitsee kentällä olevat tuntemattomat alueet turvalliseksi siten, että
    täyttö aloitetaan annetusta x, y -pisteestä.
    """
    tulva = laske_naapurit(y, x)

    for y, x in tulva:
        if (y, x) not in tarkastetut:
            tarkastetut.append((y, x))
            if tila["kentta"][y][x] != "x" and tila["esitettava_kentta"][y][x] != "f":
                tila["esitettava_kentta"][y][x] = tila["kentta"][y][x]
            if tila["kentta"][y][x] == "0":
                tulvataytto(x, y)

def kaynnista_kello():
    """
    Käynnistää kellon, joka mittaa aikaa mikä pelaajalla kuluu pelaamiseen
    """
    tila["aloitusaika"] = time.time()
    print("aloitusaika")
    print(tila["aloitusaika"])


def sammuta_kello():
    """
    Pysäyttää kellon ja tallentaa pelin keston sanakirjaan
    """
    tila["pelin_kesto"] = time.time() - tila["aloitusaika"]


def asettaja(x, y):
    """
    Asettaa lipun. Ruutua, johon on asetettu lippu, ei voida avata ennenkuin lippu poistetaan.
    """
    if tila["esitettava_kentta"][x][y] == "f":
        tila["esitettava_kentta"][x][y] = " "
        tila["lippujen_tilanne"].remove((x, y))
    elif tila["esitettava_kentta"][x][y] == " ":
        tila["esitettava_kentta"][x][y] = "f"
        tila["lippujen_tilanne"].append((x, y))
    else:
        print("Lipun asettelu epäonnistui")

    piirra_kentta()


def ruudun_avaaja(x, y):
    """
    Avaa käyttäjän valitseman ruudun.
    """
    tarkasta_havio(x, y)
    if tila["esitettava_kentta"][x][y] == " ":
        tila["vuorot"] += 1
        print("tyhjä ruutu")
        if int(tila["kentta"][x][y]) > 0:
            print("Avataan ruutu {}".format(tila["kentta"][x][y]))
            tila["esitettava_kentta"][x][y] = tila["kentta"][x][y]
            piirra_kentta()
        if tila["kentta"][x][y] == "0":
            print("nollaruutu")
            tila["esitettava_kentta"][x][y] = tila["kentta"][x][y]
            tulvataytto(y, x)
            piirra_kentta()
    tarkasta_voitto(tila["kentta"])


def numerointi(peli):
    """
    Numeroi ruudut niiden ympärillä olevien miinojen mukaiseksi
    """
    for rivin_numero, rivi in enumerate(peli):
        for sarakkeen_numero, sarake in enumerate(rivi):
            if sarake != "x":
                numerot = [peli[rivi][sarake] for rivi, sarake in laske_naapurit(
                    sarakkeen_numero, rivin_numero)]
                if numerot.count("x") > 0:
                    peli[rivin_numero][sarakkeen_numero] = str(
                        numerot.count("x"))
                else:
                    peli[rivin_numero][sarakkeen_numero] = "0"
    tila["kentta"] = peli


def tarkasta_havio(x, y):
    """
    Funktio tarkastaa hävisikö pelaaja
    """
    if tila["kentta"][x][y] == "x" and tila["esitettava_kentta"][x][y] != "f":
        tila["esitettava_kentta"] = tila["kentta"]
        tila["lopputulos"] = "Häviö"
        print("Hävisit pelin!")
        sammuta_kello()
        piirra_kentta()


def tarkasta_voitto(kentta):
    """
    Funktio tarkistaa onko avattavia ruutuja jäljellä, jos ei, pelaaja voittaa
    """
    kiinni = 0
    for rivi in kentta:
        kiinni += rivi.count(" ")  
    if kiinni == tila["miinat"]:
        return True
    return False
    

def pelin_asetukset():
    """
    Pyytää käyttäjältä peliruudukon koon sekä miinojen määrän. Funktio palauttaa kolme arvoa. Funktio tarkistaa virheelliset syötteet.
    """
    try:
        while True:
            try:
                leveys = int(
                    input("Syötä haluamasi kentän leveys (yli 1, alle 20) > "))
                if leveys < 2 or leveys > 20:
                    print("Luku ei kelpaa!")
                else:
                    break
            except ValueError:
                print("Syötä luvut kokonaislukuina!")
        while True:
            try:
                korkeus = int(
                    input("Syötä haluamasi kentän korkeus (yli 1, alle 20) > "))
                if korkeus < 2 or korkeus > 20:
                    print("Luku ei kelpaa!")
                else:
                    break
            except ValueError:
                print("Syötä luvut kokonaislukuina!")
        while True:
            try:
                miinat = int(
                    input("Syötä haluamasi miinojen määrä (yli 0, alle {}) > ".format(leveys * korkeus)))
                if miinat < 1 or miinat > leveys * korkeus:
                    print("Luku ei kelpaa!")
                else:
                    break
            except ValueError:
                print("Syötä luvut kokonaislukuina!")
        tila["leveys"] = leveys
        tila["korkeus"] = korkeus
        tila["miinojen_lkm"] = miinat
        return korkeus, leveys, miinat
    except ValueError:
        print("Syötä luvut kokonaislukuina")


def luo_kentta(korkeus, leveys, miinat):
    """
    Luo kentän
    """
    esitettava_kentta = []
    kentta = []

    for sarakkeet in range(leveys):
        kentta.append([])
        esitettava_kentta.append([])
        for rivit in range(korkeus):
            kentta[-1].append(" ")
            esitettava_kentta[-1].append(" ")

    tila["lippujen_tilanne"] = []
    tila["esitettava_kentta"] = esitettava_kentta
    tila["kentta"] = kentta

    miinoita(kentta, miinat)
    numerointi(kentta)


def tilastointi(muoto):
    """
    Funktio joko kirjoittaa tulokset tiedostoon tulokset.txt tai lukee ja tulostaa ne sieltä
    """
    if muoto == "luku":
        try:
            with open("tulokset.txt", "r") as tilasto:
                for i in tilasto:
                    kohta = i.rstrip()
                    tulos = kohta.split(",")
                    print("Aika: {}\n Kesto: {} minuuttia\n Vuorot: {}\n Lopputulos: {}\n Kentän koko: {}x{}\n Miinojen lukumäärä: {}"
                          .format(tulos[0], tulos[1], tulos[2], tulos[3], tulos[4], tulos[5], tulos[6]))
        except IOError:
            print("Virhe tulosten lukemisessa")

    if muoto == "kirjoitus":
        try:
            with open("tulokset.txt", "a") as tilasto:
                aika = time.strftime("%d.%m.%Y %H:%M", tila["paivamaara_aika"])
                print("pelin kesto")
                print(tila["pelin_kesto"])
                minuutit = int(tila["pelin_kesto"] / 60)
                print("minuutit {}".format(minuutit))
                tilasto.write("{},{},{},{},{},{},{}\n".format(
                    aika, minuutit, tila["vuorot"], tila["lopputulos"], tila["leveys"], tila["korkeus"], tila["miinojen_lkm"]))
        except IOError:
            print("Virhe tulosten tallentamisessa")

def pelivalikko():
    """
    Näyttää pelaajalle valinnat
    """
    print("1. Aloita")
    print("2. Tilastot")
    print("3. Lopeta")
    while True:
        try:
            vaihtoehto = int(input("Syötä valintasi: "))
        except ValueError:
            print("Valinta ei kelpaa")
        else:
            if vaihtoehto == 1 or vaihtoehto == 2 or vaihtoehto == 3:
                return vaihtoehto


def main():
    """
    Main-funktio luo kentän ja siihen peli-ikkunan, asettaa piirtokäsittelijän,
    asettaa hiiren käsittelijän, käynnistää ajanoton sekä aloitaa pelin.
    """
    input("Anna pelaajan nimi: ")

    valinta = pelivalikko()
    if valinta == 1:
        korkeus, leveys, miinat = pelin_asetukset()
        luo_kentta(korkeus, leveys, miinat)
        haravasto.lataa_kuvat("spritet")
        haravasto.luo_ikkuna(
            len(tila["esitettava_kentta"] * 40), len(tila["esitettava_kentta"][0] * 40))
        haravasto.aseta_piirto_kasittelija(piirra_kentta)
        haravasto.aseta_hiiri_kasittelija(kasittele_hiiri)
        kaynnista_kello()
        tila["paivamaara_aika"] = time.localtime()
        tila["vuorot"] = 0
        haravasto.aloita()
        tilastointi("kirjoitus")
    elif valinta == 2:
        tilastointi("luku")
    elif valinta == 3:
        print("Kiitos pelaamisesta")
        exit()
    else:
        print("Valintasi ei kelpaa!")


if __name__ == "__main__":
    main()

