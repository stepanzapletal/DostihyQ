# INFO
# Použít https://www.deskovehry.info/pravidla/dostihysazky.htm jako základ pravidel

# importy
import os # idk proč prostě to tam je
import random # pro hod kostkou a ostatni
import cprint # barevny print do terminalu (pip install cprint)
from cprint import *

# AI importy
# pip install ollama
# využíváme model qwen3-vl:8b protože je jednoduchý, rychlý a malý
from ollama import chat
from ollama import ChatResponse

# proměnný (neměnit! miluju upravitelny programy)
version = "0.2.3"
programName = "Qwostihy" # Dostihy + QWEN (používáme model QWEN 8b s thinking a ollamou)
preferredModel = "qwen3-vl:8b" # qwen3-vl:8b | tinyllama

# třídy
class herniPole:
    def __init__(self, typ, nazev, id, cena=None, vlastnik=None, odmenaZaStart=None, druh=None, platba=None, cisloTrenera=None, dostihy=None):
        # možné typy: start, kun, finance, nahoda, veterina, trener, distanc, preprava, parkoviste, staje, doping
        self.typ = typ
        self.nazev = nazev
        self.id = id
        if typ=="start":
            # startovni pole
            self.odmenaZaStart = odmenaZaStart
        elif typ=="kun":
            self.cena = cena
            self.vlastnik = vlastnik
            self.druh = druh # druh koně (nazev a atributy)
            self.dostihy = dostihy # počet dostihů, které na daném poli jsou (0 - 4 základní dostihy, 5 = hlavní (červený) dostih)
        elif typ=="finance":
            pass # finance
        elif typ=="nahoda":
            pass # nahoda
        elif typ=="veterina":
            self.platba = platba
        elif typ=="trener":
            self.cena = cena
            self.vlastnik = vlastnik
            self.cisloTrenera = cisloTrenera
        elif typ=="distanc":
            pass # distanc
        elif typ=="preprava":
            self.cena = cena
            self.vlastnik = vlastnik
        elif typ=="staje":
            self.cena = cena
            self.vlastnik = vlastnik
        elif typ=="parkoviste":
            pass # nic se tam nedeje
        elif typ=="doping":
            pass # doping
    def __repr__(self): # reprodukce
        # format pro tisk do AIka
        params = f"typ='{self.typ}', nazev='{self.nazev}', id='{self.id}'"
        
        if hasattr(self, 'odmenaZaStart') and self.odmenaZaStart is not None:
            params += f", odmenaZaStart={self.odmenaZaStart}"
        if hasattr(self, 'cena') and self.cena is not None:
            params += f", cena={self.cena}"
        if hasattr(self, 'vlastnik') and self.vlastnik is not None:
            params += f", vlastnik={repr(self.vlastnik)}"
        if hasattr(self, 'druh') and self.druh is not None:
            params += f", druh='{self.druh}'"
        if hasattr(self, 'dostihy') and self.dostihy is not None:
            params += f", dostihy={self.dostihy}"
        if hasattr(self, 'platba') and self.platba is not None:
            params += f", platba={self.platba}"
        if hasattr(self, 'cisloTrenera') and self.cisloTrenera is not None:
            params += f", cisloTrenera={self.cisloTrenera}"
        return f"herniPole({params})"

class hrac:
    def __init__(self, jmeno, cisloHrace, penize, jeAI=False):
        self.jmeno = jmeno
        self.cisloHrace = cisloHrace
        self.penize = penize # počáteční peníze
        self.jeAI = jeAI
        #self.kone = [] # seznam vlastněných koní
        #self.treneri = [] # seznam vlastněných trenérů
        #self.ostatniKarty = [] # seznam ostatních karet (přeprava koní atd.)
        self.pozice = 0 # pozice na herní desce (0 je startovni pole)
        self.maKartuPrycZDistancu = False # jestli má kartu na zrušení distancu (mohou ji mit oba hráči)
        self.jeNaDistancu = False # jestli je na distancu
        self.kolikKolNehraje = 0 # počet kol, které hráč vynechává (např. doping)

financeDict = {
    "platba1000" : "Zaplať pojistku 1000.", 
    "platba400" : "Pokuta za nedodržení předpisů 400.", 
    "dostihy500" : "Renovuješ všechny stáje. Za každý svůj obsazený dostih zaplať 500.",
    "plus2000" : "Mimořádný zisk z dostihů obdržíš 2.000.", 
    "darek200" : "Jako dárek k narozeninám obdržíš od každého 200.",
    "plus500" : "Mimořádná prémie 500.", 
    "plus4000" : "Obdržíš dotaci 4.000.", 
    "platba3000" : "Zaplať dluh 3.000.", 
    "dostihy800_2300" : "Za každý svůj obsazený dostih zaplať 800, za každý svůj obsazený hlavní dostih sezóny zaplať 2.300.",
    "platba2000" : "Zaplať příspěvek 2.000.", 
    "platba100" : "Nákup materiálu na opravu 100.", 
    "plus1000" : "Výhra v loterii 1.000.",
    "plus2000" : "Obdržíš dotaci 2.000.", 
    "plus3000" : "Z banky obdržíš přeplatek 3.000."
}

nahodyDict = {
    "zpet3" : "Jdi o 3 pole zpět.",
    "bezdistancu" : "Zrušen distanc (kartu lze zachovat pro pozdější použití, nebo prodat).",
    "trenerdopredu4000" : "Jedeš se zúčastnit trenérského kurzu. Postoupíš na nejbližší pole Trenér. Dostaneš 4.000, pokud jedeš dopředu přes Start.",
    "distancbez4000" : "Distanc (bez 4.000).",
    "zpetnapoli4000" : "Zpět na poslední pole ve hře (kůň Napoli), hráč obdrží 4.000.",
    "zpetdistanc" : "Zpět na pole Distanc. Obdržíš 4.000, pokud jsi cestou zpět prošel Start.",
    "finance" : "Zpět na nejbližší pole Finance.",
    "start4000" : "Zpět na start (hráč obdrží 4.000).",
    "startbez4000" : "Zpět na start (bez 4.000).",
    "pauza2" : "Zdržíš se na 2 kola.",
    "pauza1" : "Zdržíš se na 1 kolo.",
    "zpetparkoviste" : "Zpět na pole Parkoviště. Dostaneš 4.000, pokud jsi cestou zpět prošel start."
}

koneDict = {

    "Fantome": {
        "koneVeStaji": ["Fantome", "Gavora"],
        "poplatek": 40,
        "platbyZaDostihy": [200, 600, 1800, 3200, 5000],  # index 0 = 1. dostih, index 4 = hlavní dostih
        "cenaZaDostih": 1000
    },
    "Gavora": {
        "koneVeStaji": ["Fantome", "Gavora"],
        "poplatek": 40,
        "platbyZaDostihy": [200, 600, 1800, 3200, 5000],  # index 0 = 1. dostih, index 4 = hlavní dostih
        "cenaZaDostih": 1000
    },

    "Lady Anne": {
        "koneVeStaji": ["Lady Anne", "Pasek", "Koran"],
        "poplatek": 120,
        "platbyZaDostihy": [600, 1800, 5400, 8000, 11000],  # index 0 = 1. dostih, index 4 = hlavní dostih
        "cenaZaDostih": 1000
    },
    "Pasek": {
        "koneVeStaji": ["Lady Anne", "Pasek", "Koran"],
        "poplatek": 120,
        "platbyZaDostihy": [600, 1800, 5400, 8000, 11000],  # index 0 = 1. dostih, index 4 = hlavní dostih
        "cenaZaDostih": 1000
    },
    "Koran": {
        "koneVeStaji": ["Lady Anne", "Pasek", "Koran"],
        "poplatek": 160,
        "platbyZaDostihy": [800, 2000, 6000, 9000, 12000],  # index 0 = 1. dostih, index 4 = hlavní dostih
        "cenaZaDostih": 1000
    },

    "Neklan": {
        "koneVeStaji": ["Neklan", "Portlancl", "Japan"],
        "poplatek": 200,
        "platbyZaDostihy": [1000, 3000, 9000, 12500, 15000],  # index 0 = 1. dostih, index 4 = hlavní dostih
        "cenaZaDostih": 2000
    },
    "Portlancl": {
        "koneVeStaji": ["Neklan", "Portlancl", "Japan"],
        "poplatek": 200,
        "platbyZaDostihy": [1000, 3000, 9000, 12500, 15000],  # index 0 = 1. dostih, index 4 = hlavní dostih
        "cenaZaDostih": 2000
    },
    "Japan": {
        "koneVeStaji": ["Neklan", "Portlancl", "Japan"],
        "poplatek": 240,
        "platbyZaDostihy": [1200, 3600, 10000, 14000, 18000],  # index 0 = 1. dostih, index 4 = hlavní dostih
        "cenaZaDostih": 2000
    },

    "Kostrava": {
        "koneVeStaji": ["Kostrava", "Lukava", "Melák"],
        "poplatek": 280,
        "platbyZaDostihy": [1400, 4000, 11000, 15000, 19000],  # index 0 = 1. dostih, index 4 = hlavní dostih
        "cenaZaDostih": 2000
    },
    "Lukava": {
        "koneVeStaji": ["Kostrava", "Lukava", "Melák"],
        "poplatek": 280,
        "platbyZaDostihy": [1400, 4000, 11000, 15000, 19000],  # index 0 = 1. dostih, index 4 = hlavní dostih
        "cenaZaDostih": 2000
    },
    "Melák": {
        "koneVeStaji": ["Kostrava", "Lukava", "Melák"],
        "poplatek": 320,
        "platbyZaDostihy": [1600, 4400, 12000, 16000, 20000],  # index 0 = 1. dostih, index 4 = hlavní dostih
        "cenaZaDostih": 2000
    },

    "Grifel": {
        "koneVeStaji": ["Grifel", "Mohyla", "Metál"],
        "poplatek": 360,
        "platbyZaDostihy": [1800, 5000, 14000, 17000, 21000],  # index 0 = 1. dostih, index 4 = hlavní dostih
        "cenaZaDostih": 3000
    },
    "Mohyla": {
        "koneVeStaji": ["Grifel", "Mohyla", "Metál"],
        "poplatek": 360,
        "platbyZaDostihy": [1800, 5000, 14000, 17000, 21000],  # index 0 = 1. dostih, index 4 = hlavní dostih
        "cenaZaDostih": 3000
    },
    "Metál": {
        "koneVeStaji": ["Grifel", "Mohyla", "Metál"],
        "poplatek": 400,
        "platbyZaDostihy": [2000, 6000, 15000, 18000, 22000],  # index 0 = 1. dostih, index 4 = hlavní dostih
        "cenaZaDostih": 3000
    },

    "Tara": {
        "koneVeStaji": ["Tara", "Furioso", "Genius"],
        "poplatek": 440,
        "platbyZaDostihy": [2200, 6600, 16000, 19500, 23000],  # index 0 = 1. dostih, index 4 = hlavní dostih
        "cenaZaDostih": 3000
    },
    "Furioso": {
        "koneVeStaji": ["Tara", "Furioso", "Genius"],
        "poplatek": 440,
        "platbyZaDostihy": [2200, 6600, 16000, 19500, 23000],  # index 0 = 1. dostih, index 4 = hlavní dostih
        "cenaZaDostih": 3000
    },
    "Genius": {
        "koneVeStaji": ["Tara", "Furioso", "Genius"],
        "poplatek": 580,
        "platbyZaDostihy": [2400, 7200, 17000, 20500, 24000],  # index 0 = 1. dostih, index 4 = hlavní dostih
        "cenaZaDostih": 3000
    },

    "Shagga": {
        "koneVeStaji": ["Shagga", "Dahoman", "Gira"],
        "poplatek": 500,
        "platbyZaDostihy": [2600, 7800, 18000, 22000, 25500],  # index 0 = 1. dostih, index 4 = hlavní dostih
        "cenaZaDostih": 4000
    },
    "Dahoman": {
        "koneVeStaji": ["Shagga", "Dahoman", "Gira"],
        "poplatek": 500,
        "platbyZaDostihy": [2600, 7800, 18000, 22000, 25500],  # index 0 = 1. dostih, index 4 = hlavní dostih
        "cenaZaDostih": 4000
    },
    "Gira": {
        "koneVeStaji": ["Shagga", "Dahoman", "Gira"],
        "poplatek": 560,
        "platbyZaDostihy": [3000, 9000, 20000, 24000, 28000],  # index 0 = 1. dostih, index 4 = hlavní dostih
        "cenaZaDostih": 4000
    },

    "Narcius": {
        "koneVeStaji": ["Narcius", "Napoli"],
        "poplatek": 700,
        "platbyZaDostihy": [3500, 10000, 22000, 26000, 30000],  # index 0 = 1. dostih, index 4 = hlavní dostih
        "cenaZaDostih": 4000
    },
    "Napoli": {
        "koneVeStaji": ["Narcius", "Napoli"],
        "poplatek": 1000,
        "platbyZaDostihy": [4000, 12000, 28000, 34000, 40000],  # index 0 = 1. dostih, index 4 = hlavní dostih
        "cenaZaDostih": 4000
    }
}

#herniDeska = [ # Základní herní deska
#    herniPole("start", "Start", "start", odmenaZaStart=2000),
#    herniPole("kun", "Kůn Michal", "testkun", vlastnik=None, cena=1500, druh="Michal"),
#    herniPole("kun", "Kůn Tomáš", "tomaskun", vlastnik=None, cena=3000, druh="Tomáš"),
#    herniPole("finance", "Finance", "finance1"),
#    herniPole("nahoda", "Náhoda", "nahoda1"),
#    herniPole("veterina", "Veterinární ošetření", "veterina", platba=1000),
#    herniPole("trener", "Trenér č.1", "trener1", vlastnik=None, cena=2000, cisloTrenera=1),
#    herniPole("trener", "Trenér č.2", "trener2", vlastnik=None, cena=2000, cisloTrenera=2),
#    herniPole("distanc", "Distanc #1", "distanc1"),
#    herniPole("preprava", "Přeprava koní", "testpreprava", vlastnik=None, cena=1500),
#    herniPole("parkoviste", "Parkoviště", "parkoviste1"),
#    herniPole("staje", "Stáje č.1", "staje1", vlastnik=None, cena=2500),
#    herniPole("doping", "Dopingová kontrola", "doping1"),
#    herniPole("kun", "Kůn Narcius", "narcius", vlastnik=None, cena=7000, druh="Narcius"),
#    herniPole("kun", "Kůn Napoli", "napoli", vlastnik=None, cena=8000, druh="Napoli")
#]

herniDeska = [ # Actual herní deska
    herniPole("start", "Start", "start", odmenaZaStart=4000),
    herniPole("kun", "Kůň Fantome", "fantomekun", vlastnik=None, cena=1200, druh="Fantome"),
    herniPole("finance", "Finance", "finance1"),
    herniPole("kun", "Kůň Gavora", "gavorakun", vlastnik=None, cena=1200, druh="Gavora"),
    herniPole("veterina", "Veterinární vyšetření", "veterina1", platba=500),
    herniPole("trener", "Trenér č.1", "trener1", vlastnik=None, cena=4000, cisloTrenera=1),
    herniPole("kun", "Kůň Lady Anne", "ladyannekun", vlastnik=None, cena=2000, druh="Lady Anne"),
    herniPole("nahoda", "Náhoda", "nahoda1"),
    herniPole("kun", "Kůň Pasek", "pasekkun", vlastnik=None, cena=2000, druh="Pasek"),
    herniPole("kun", "Kůň Koran", "korankun", vlastnik=None, cena=2400, druh="Koran"),
    herniPole("distanc", "Distanc", "distanc1"),
    herniPole("kun", "Kůň Neklan", "neklankun", vlastnik=None, cena=2800, druh="Neklan"),
    herniPole("preprava", "Přeprava", "preprava", vlastnik=None, cena=3000),
    herniPole("kun", "Kůň Portlancl", "portlanclkun", vlastnik=None, cena=2800, druh="Portlancl"),
    herniPole("kun", "Kůň Japan", "japankun", vlastnik=None, cena=2800, druh="Japan"),
    herniPole("trener", "Trenér č.2", "trener2", vlastnik=None, cena=4000, cisloTrenera=2),
    herniPole("kun", "Kůň Kostrava", "kostravakun", vlastnik=None, cena=3600, druh="Kostrava"),
    herniPole("finance", "Finance", "finance2"),
    herniPole("kun", "Kůň Lukava", "lukavakun", vlastnik=None, cena=3600, druh="Lukava"),
    herniPole("kun", "Kůň Melák", "melakkun", vlastnik=None, cena=4000, druh="Melák"),
    herniPole("parkoviste", "Parkoviště", "parkoviste1"),
    herniPole("kun", "Kůň Grifel", "grifelkun", vlastnik=None, cena=4400, druh="Grifel"),
    herniPole("nahoda", "Náhoda", "nahoda2"),
    herniPole("kun", "Kůň Mohyla", "mohylakun", vlastnik=None, cena=4400, druh="Mohyla"),
    herniPole("kun", "Kůň Metál", "metalkun", vlastnik=None, cena=4800, druh="Metál"),
    herniPole("trener", "Trenér č.3", "trener3", vlastnik=None, cena=4000, cisloTrenera=3),
    herniPole("kun", "Kůň Tara", "tarakun", vlastnik=None, cena=5200, druh="Tara"),
    herniPole("kun", "Kůň Furioso", "furiosokun", vlastnik=None, cena=5200, druh="Furioso"),
    herniPole("staje", "Stáje", "staje1", vlastnik=None, cena=3000),
    herniPole("kun", "Kůň Genius", "geniuskun", vlastnik=None, cena=5600, druh="Genius"),
    herniPole("doping", "Podezření z dopingu", "doping1"),
    herniPole("kun", "Kůň Shagga", "shaggakun", vlastnik=None, cena=6000, druh="Shagga"),
    herniPole("kun", "Kůň Dahoman", "dahomankun", vlastnik=None, cena=6000, druh="Dahoman"),
    herniPole("finance", "Finance", "finance3"),
    herniPole("kun", "Kůň Gira", "girakun", vlastnik=None, cena=6400, druh="Gira"),
    herniPole("trener", "Trenér č.4", "trener4", vlastnik=None, cena=4000, cisloTrenera=4),
    herniPole("nahoda", "Náhoda", "nahoda3"),
    herniPole("kun", "Kůn Narcius", "narcius", vlastnik=None, cena=7000, druh="Narcius"),
    herniPole("veterina", "Veterinární vyšetření", "veterina2", platba=1000),
    herniPole("kun", "Kůn Napoli", "napoli", vlastnik=None, cena=8000, druh="Napoli")
]

# Redundancy check jestli jsou vsechny kone v koneDict
for pole in herniDeska:
    if pole.typ == "kun":
        if pole.druh not in koneDict:
            print(f"Chyba: Kůň {pole.druh} na poli {pole.nazev} není v koneDict!")
            exit()

# redundancy check jestli na desce neni vic nez jedna preprava a staje
pocetPreprav = 0
pocetStaji = 0
for pole in herniDeska:
    if pole.typ == "preprava":
        pocetPreprav += 1
    if pole.typ == "staje":
        pocetStaji += 1
if pocetPreprav > 1:
    print("Chyba: Na herní desce je více než jedno pole přepravy!")
    exit()
if pocetStaji > 1:
    print("Chyba: Na herní desce je více než jedno pole stájí!")
    exit()

# počet hráčů
pocetHracu = 2 # počet hráčů (hardcoded)
pocetTreneruNaDesce = None # vypocitat
for pole in herniDeska:
    if pole.typ == "trener":
        pocetTreneruNaDesce = max(pocetTreneruNaDesce or 0, pole.cisloTrenera)
        #print(pocetTreneruNaDesce) # debug


hraci = [ # Definice hráčů
    hrac("Hráč 1 (humanoid)", 1, 30000, False),
    hrac("Hráč 2 (AI)", 2, 30000, True)
]

def bankrot():
    print("Jsi v bankrotu! Konec hry") # je potřeba dodělat prodávání majetku atd.
    exit()

# sestavit layout desky pro AI
layoutDesky = ""
for pole in herniDeska:
    layoutDesky += repr(pole) + "\n"
print(str(koneDict))
systemPromptBehavior = """You are an assistant for the board a game called "Dostihy a sázky" (Czech Horse Racing and Betting). Your purpose is to win the game at all costs.
You will be playing against human players. You must make decisions based on the current game state and your strategy to win.

When making decisions, consider the following:
The game will roll the dice for you, you will be informed about how the game board looks like, your current position, money, owned properties (horses, trainers, stables, transport etc.) and other players' positions and money and etc.
You must decide what to do based on this information. You will be asked about your decisions during your turn. For example, if you want to buy a horse or buy a "dostih" (which is basically a multiplier for money).

Below is the default configuration of the game board (this will NOT change):
""" + str(layoutDesky) + """
Also, here is the dictionary of horses and their attributes:
""" + str(koneDict) + """
The game rules are based on the official rules of "Dostihy a sázky", however some rules may be simplified for the sake of this implementation. But the core mechanics remain the same.
Your goal is to maximize your money and assets while minimizing losses. You can buy horses, trainers, stables, and transport to increase your income from other players landing on your properties.
If you land on finance or random event fields, the game will inform you about the event which had been chosen at random.
You begin with 30000 money.

You should always form your responses very simply. You may use advanced language when thinking, but NEVER in your final answers. Your final answers should be very simple, stripped of any grammar. For example a simple a/n answer is required, or a number (1-5, you will always be informed about the range).
If you fail to respond in the required format, you will be reminded to do so and re-queried, slowing you down.
Strategize carefully and think multiple steps ahead. Consider the potential moves of your opponents and how you can counter them. Strategizing should be done when thinking, and NEVER respond with anything other than requested in the final answer.
Remember, your ultimate goal is to win the game. Make decisions that will lead you to victory.

Good Luck!"""
msgHistory = [
    {"role": "system", "content": systemPromptBehavior},
] # historie zpráv pro AI aby věděla co se děje
def queryAI(userprompt):
    global msgHistory
    msgHistory.append({"role": "user", "content": userprompt}) # přidat uživatelskou zprávu do historie
    response: ChatResponse = chat(
        model=preferredModel,
        messages=msgHistory, # předat historii zpráv + novou zprávu
        think=True,  # zažádat o "think" režim
    )
    return response

def brainwashAI():
    global msgHistory
    msgHistory = [
        {"role": "system", "content": systemPromptBehavior},
    ] # reset historie zpráv pro AI

brainwashAI() # inicializovat AI historii zpráv
# jak jej vypsat dobře a čitelně?

# zkontrolovat funkci AI jednoduchou otázkou
beginQuery = """"
Zda-li jsi schopen porozumět tomuto textu a odpovědět pouze "ano" nebo "ne"? Tím začne hra. Odpověž pouze ano, nebo ne."""
print("Kontrola AI... Může to trvat až 5 minut (podle toho jestli pracujeme na CPU či GPU)...")
beginQ = queryAI(beginQuery)
if "ano" not in beginQ.message.content.lower():
    print("Response ERROR: "+beginQ.message.thinking + "\nVýsledek: " + beginQ.message.content)
    exit()
else:
    print("AI je připravena hrát hru! (Odpověď: " + beginQ.message.content + " s myšlením: " + beginQ.message.thinking + ")")


# zakladni gameplay loop
while True:
    for player in hraci:
        #if player.jeAI:
        #    # informovat AI o stavu desky
        #    infoMsg = f"Aktuální stav hry:\n{str(herniDeska)}\n. Pro pokračování na další kolo a podtvrzení, že stav hry chápeš napiš 'a'"
        #    isAiOk = queryAI(infoMsg)
        #    if "a" not in isAiOk.message.content.lower(): # AI není v poho
        #        print("Response ERROR: "+isAiOk.message.thinking + "\nVýsledek: " + isAiOk.message.content)
        #        exit()
        #    print(f"AI informována o stavu desky: {isAiOk.message.content} s myšlením: {isAiOk.message.thinking}")
        # dočasná proměnná pro zrušení distancu
        tempNeniNaDistancu = False
        # check jestli hrac nehraje (doping atd.)
        if player.kolikKolNehraje > 0:
            print(f"{player.jmeno} se zdrží o {player.kolikKolNehraje} kola.")
            player.kolikKolNehraje -= 1
            continue # preskocit tento tah
        print(f"Nyní hraje {player.jmeno} s {player.penize} penězi na pozici {player.pozice} na poli {herniDeska[player.pozice].nazev}.")
        # pokud je na distancu, tak musi mit 6 aby se posunul
        if herniDeska[player.pozice].typ == "distanc":
            if player.maKartuPrycZDistancu:
                chceJiPouzit = input("Jsi na distancu, ale máš kartu na zrušení distancu. Chceš ji použít? (a/n): ")
                if chceJiPouzit.lower() == "a":
                    print("Použil jsi kartu na zrušení distancu.")
                    player.maKartuPrycZDistancu = False
                    tempNeniNaDistancu = True
                else:
                    print("Nepoužil jsi kartu na zrušení distancu.")
        # hod kostkou
        if not player.jeAI:
            input("Stiskni Enter pro hod kostkou...")
        else:
            # Není AI logika pro rozhodnutí o hodu kostkou, protože hod kostkou je náhodný proces
            pass
        hod = random.randint(1, 6)
        print(f"Hráč {player.jmeno} hodil {hod}!")
        # pokud je na distancu, tak musi mit 6 aby se posunul
        if hod == 6 and not tempNeniNaDistancu and herniDeska[player.pozice].typ == "distanc":
            print("Hodil jsi 6 na distancu, můžeš hodit znovu a posunout se!")
            if not player.jeAI:
                # hod kostkou
                input("Stiskni Enter pro hod kostkou...")
            else:
                # Není potřeba AI logika pro rozhodnutí o hodu kostkou, protože hod kostkou je náhodný proces
                pass
            hod = random.randint(1, 6)
            print(f"Hráč {player.jmeno} hodil {hod}!")
        elif tempNeniNaDistancu and herniDeska[player.pozice].typ == "distanc":
            print("Jsi nyní mimo distanc, můžeš se posunout normálně.")
        elif herniDeska[player.pozice].typ == "distanc":
            print("Nehodil si 6 a stojíš na distancu! Neposouváš se.")
            continue # preskocit tento tah
        if hod == 6:
            print("Můžeš hodit znovu po dokončení tahu.")
            if not player.jeAI:
                # hod kostkou
                input("Stiskni Enter pro hod kostkou...")
            else:
                # jezis je to nahodny
                pass
            hod = hod + random.randint(1, 6)
            if hod == 12:
                # DISTANC = 6 + 6
                print("Hodil jsi další 6! Posouváš se na distanc.")
                # najít distanc
                for i in range(len(herniDeska)):
                    if herniDeska[i].typ == "distanc":
                        poziceDistanc = i
                        break
                hod = poziceDistanc - player.pozice # posun na distanc
            else:
                print(f"Dohromady jsi hodil {hod}!")
        
        # posun na desce
        
        player.pozice = (player.pozice + hod) # zatím neřešíme přetočení desky
        if player.pozice >= len(herniDeska): # prošel jsi startem
            player.pozice = player.pozice - len(herniDeska)
            player.penize += herniDeska[0].odmenaZaStart # odměna za start
            print(f"Prošel jsi Startem a získal {herniDeska[0].odmenaZaStart} peněz!")
            # aby pozice nebyla v minusu
            if player.pozice < 0:
                player.pozice = len(herniDeska) + player.pozice

        aktualniPole = herniDeska[player.pozice]
        print(f"Stojíš na poli: {aktualniPole.nazev}")
        print(f"Pole typu: {aktualniPole.typ}")
        
        # check typ pole
        # ==============
        # POLE TYPU KONĚ
        # ==============
        if aktualniPole.typ == "kun": # kdyz je to kun
            if aktualniPole.vlastnik is None: # a nema vlastnika
                print(f"Tento kůň stojí {aktualniPole.cena} peněz.")
                if not player.jeAI:
                    koupit = input("Chceš si ho koupit? (a/n): ")
                else:
                    queryAIMsg = f"Jsi na poli s koněm {aktualniPole.nazev} který stojí {aktualniPole.cena} peněz a nemá vlastníka. Máš {player.penize} peněz. Chceš si tohoto koně koupit? Odpověž pouze 'a' pro ano nebo 'n' pro ne."
                    aiResponse = queryAI(queryAIMsg)
                    koupit = aiResponse.message.content.strip().lower()
                    print(f"AI odpověděla: {koupit} (s myšlením: {aiResponse.message.thinking})")
                if koupit.lower() == "a": # hrac se ho rozhodl koupit
                    if player.penize >= aktualniPole.cena: # ma dost penez?
                        player.penize -= aktualniPole.cena # odecist penize
                        aktualniPole.vlastnik = player.cisloHrace # nastavit vlastnika
                        print(f"Koupil jsi koně {aktualniPole.nazev}!")

                    else: # nema dost penez...
                        print("Nemáš dost peněz na koupi tohoto koně.")

                else: # nechce
                    print("Rozhodl jsi se koně nekoupit.")
            else: # uz ma vlastnika
                if aktualniPole.vlastnik == player.cisloHrace:  # Je to muj kůň
                    # získat koně na desce z aktivni staje
                    koneVeStaji = koneDict[aktualniPole.druh]["koneVeStaji"]
                    # vsechny kone co hrac ma
                    koneCoMam = []
                    for pole in herniDeska:
                        if pole.typ == "kun" and pole.vlastnik == player.cisloHrace:
                            koneCoMam.append(pole.druh)
                    # zkontrolovat jestli ma vsechny kone ve staji
                    vlastniVsechny = True
                    chybiKone = []
                    for kunVeStaji in koneVeStaji:
                        if kunVeStaji not in koneCoMam:
                            vlastniVsechny = False
                            chybiKone.append(kunVeStaji)
                            break
                    if vlastniVsechny: # Má všechny koně, lze koupit dostihy
                        maxDostihu = 4 # maximalni pocet dostihu
                        if aktualniPole.dostihy is None: 
                            aktualniPole.dostihy = 0
                        if aktualniPole.dostihy < maxDostihu:
                            print(f"Můžeš koupit dostih pro tohoto koně. Cena za dostih je {koneDict[aktualniPole.druh]['cenaZaDostih']} peněz.")
                            if not player.jeAI:
                                koupitDostih = input("Chceš koupit dostih? (a/n): ")
                            else:
                                chceMsg = f"Jsi na svém koni {aktualniPole.nazev} který má {aktualniPole.dostihy} dostihů. Můžeš koupit další dostih za {koneDict[aktualniPole.druh]['cenaZaDostih']} peněz. Máš {player.penize} peněz. Chceš koupit dostih? Odpověž pouze 'a' pro ano nebo 'n' pro ne."
                                aiResponse = queryAI(chceMsg)
                                koupitDostih = aiResponse.message.content.strip().lower()
                                print(f"AI odpověděla: {koupitDostih} (s myšlením: {aiResponse.message.thinking})")
                            if koupitDostih.lower() == "a":
                                if player.penize >= koneDict[aktualniPole.druh]["cenaZaDostih"]:
                                    kolikDostihuChce = int(input(f"Kolik dostihů chceš koupit? (max {maxDostihu - aktualniPole.dostihy}): "))
                                    player.penize -= koneDict[aktualniPole.druh]["cenaZaDostih"]*kolikDostihuChce
                                    aktualniPole.dostihy += kolikDostihuChce
                                    print(f"Koupil jsi dostih pro koně {aktualniPole.nazev}. Nyní má {aktualniPole.dostihy} dostihů.")
                                else:
                                    print("Nemáš dost peněz na koupi dostihu.")
                            else:
                                print("Rozhodl jsi se nekoupit dostih.")
                        else:
                            print("Tento kůň již má maximální počet dostihů. Chceš si koupit hlavní dostih?")
                            if not player.jeAI:
                                koupitHlavniDostih = input("Chceš koupit hlavní dostih? (a/n): ")
                            else:
                                hDostihMsg = f"Jsi na svém koni {aktualniPole.nazev} který má maximální počet dostihů. Můžeš koupit hlavní dostih za {koneDict[aktualniPole.druh]['cenaZaDostih']} peněz. Máš {player.penize} peněz. Chceš koupit hlavní dostih? Odpověž pouze 'a' pro ano nebo 'n' pro ne."
                                aiResponse = queryAI(hDostihMsg)
                                koupitHlavniDostih = aiResponse.message.content.strip().lower()
                                print(f"AI odpověděla: {koupitHlavniDostih} (s myšlením: {aiResponse.message.thinking})")
                            if koupitHlavniDostih.lower() == "a":
                                if player.penize >= koneDict[aktualniPole.druh]["cenaZaDostih"]:
                                    player.penize -= koneDict[aktualniPole.druh]["cenaZaDostih"]
                                    aktualniPole.dostihy = 5 # hlavní dostih
                                    print(f"Koupil jsi hlavní dostih pro koně {aktualniPole.nazev}. Předchozí 4 dostihy byly nahrazeny jedním hlavním dostihem.")
                                else:
                                    print("Nemáš dost peněz na koupi hlavního dostihu.")
                            
                    else: # nema vsechny
                        print(f"Aby jsi mohl kupovat dostihy, musíš vlastnit všechny koně této stáje. Chybí ti: {', '.join(chybiKone)}")

                elif aktualniPole.vlastnik != player.cisloHrace: # neni to muj kun
                    print(str(hraci[aktualniPole.vlastnik-1].jeNaDistancu))
                    print(str(hraci[aktualniPole.vlastnik-1].jmeno))
                    druhKone = aktualniPole.druh
                    # check kolik ma kun dostihu (pokud nula tak zakladni poplatek)
                    if aktualniPole.dostihy is None or hraci[aktualniPole.vlastnik-1].jeNaDistancu: # pokud je na distancu, tak plati zakladni poplatek
                        poplatek = koneDict[druhKone]["poplatek"]
                    else:
                        pocetDostihu = aktualniPole.dostihy
                        poplatek = koneDict[druhKone]["platbyZaDostihy"][pocetDostihu - 1] # -1 protoze indexy jsou od 0 a dostihy jsou od 1
                    print(f"Tento kůň patří hráči {aktualniPole.vlastnik}. Musíš mu zaplatit poplatek {poplatek} peněz.")
                    if not player.jeAI:
                        input("Stiskni Enter pro zaplacení poplatku...")
                    else:
                        # Není potřeba dávat query na AI protože to je jen platba
                        pass
                    if player.penize >= poplatek: # má dost peněz na poplatek
                        player.penize -= poplatek # odčíst peníze
                        for hracVlastnik in hraci: # najit vlastnika a prict penize
                            if hracVlastnik.cisloHrace == aktualniPole.vlastnik:
                                hracVlastnik.penize += poplatek
                                print(f"Zaplatil jsi {poplatek} peněz hráči {hracVlastnik.jmeno}.")
                                break
                    else:
                        print("Nemáš dost peněz na zaplacení poplatku!")
                        bankrot()
        # =================
        # POLE TYPU FINANCE
        # =================
        if aktualniPole.typ == "finance":
            # vyber náhodnou kartu z financí
            karta = random.choice(list(financeDict.keys()))
            print(f"Finance karta: {financeDict[karta]}")
            # zpracování karty
            if "platba" in karta:
                castka = int(karta.replace("platba", ""))
                if player.penize >= castka:
                    player.penize -= castka
                    print(f"Zaplatil jsi bance {castka} peněz.")
                else:
                    print("Nemáš dost peněz na zaplacení této částky!")
                    bankrot()
            elif "plus" in karta:
                castka = int(karta.replace("plus", ""))
                player.penize += castka
                print(f"Obdržel jsi od banky {castka} peněz.")
            elif "darek" in karta:
                castka = int(karta.replace("darek", ""))
                totalDarek = castka * (pocetHracu - 1)
                player.penize += totalDarek
                # odecist ostatnim
                for ostatniHrac in hraci:
                    if ostatniHrac.cisloHrace != player.cisloHrace:
                        if ostatniHrac.penize >= castka:
                            ostatniHrac.penize -= castka
                        else:
                            print(f"Hráč {ostatniHrac.jmeno} nemá dost peněz na zaplacení dárku!")
                            bankrot()
                print(f"Obdržel jsi od ostatních hráčů celkem {totalDarek} peněz.")
            elif "dostihy" in karta:
                castka = int(karta.replace("dostihy", ""))
                if "_" in str(castka):
                    # platba s dostihy a hlavní dostihy
                    castky = karta.split("_") # rozdelit na dve castky 800 a 2300
                    castkaDostihy = int(castky[0])
                    castkaHlavniDostihy = int(castky[1])
                    totalPlatba = 0
                    for pole in herniDeska: # pro kazde pole
                        if pole.typ == "kun" and pole.vlastnik == player.cisloHrace: # ktere je moje
                            if pole.dostihy is not None and pole.dostihy > 0 and pole.dostihy != 5: # a ma dostihy (ale ne hlavni)
                                totalPlatba += castkaDostihy*pole.dostihy # zaplatit za kazdy dostih
                            elif pole.dostihy == 5: # hlavni dostih
                                totalPlatba += castkaHlavniDostihy
                    if player.penize >= totalPlatba:
                        player.penize -= totalPlatba
                        print(f"Zaplatil jsi celkem {totalPlatba} peněz za své dostihy.")
                else:
                    totalPlatba = 0
                    for pole in herniDeska: # pro kazde pole
                        if pole.typ == "kun" and pole.vlastnik == player.cisloHrace: # ktere je moje
                            if pole.dostihy is not None and pole.dostihy > 0 and pole.dostihy != 5: # a ma dostihy (ale ne hlavni)
                                totalPlatba += castka*pole.dostihy # zaplatit za kazdy dostih
                    if player.penize >= totalPlatba:
                        player.penize -= totalPlatba
                        print(f"Zaplatil jsi celkem {totalPlatba} peněz za své dostihy.")
                    else:
                        print("Nemáš dost peněz na zaplacení této částky!")
                        bankrot()
        # ================
        # POLE TYPU NÁHODA
        # ================
        elif aktualniPole.typ == "nahoda":
            # vyber náhodnou kartu z náhody
            karta = random.choice(list(nahodyDict.keys()))
            print(f"Náhoda karta: {nahodyDict[karta]}")
            # zpracování karty
            if "zpet3" in karta:
                player.pozice -= 3
                if player.pozice < 0:
                    player.pozice = len(herniDeska) + player.pozice
                print(f"Vracíš se o 3 pole zpět na pole {herniDeska[player.pozice].nazev}.")
            elif "bezdistancu" in karta:
                player.maKartuPrycZDistancu = True
                print("Získal jsi kartu na zrušení distancu.")
            elif "trenerdopredu4000" in karta:
                # najit nejblizsi trener pole
                nejblizsiTrenerPozice = None
                for i in range(1, len(herniDeska)): # projit vsechna pole
                    poziceCheck = (player.pozice + i) % len(herniDeska) # pozice ktera se kontroluje
                    if herniDeska[poziceCheck].typ == "trener": # jestli je to trener
                        nejblizsiTrenerPozice = poziceCheck
                        break # nasel jsme nejblizsiho trenéra
                if nejblizsiTrenerPozice is not None: # nasel jsme nejblizsiho trenéra
                    # check jestli presel start
                    if nejblizsiTrenerPozice > player.pozice: # presel start
                        player.penize += 4000 # dostane 4000
                        print("Prošel jsi Startem a získal 4.000 peněz!")
                    player.pozice = nejblizsiTrenerPozice
                    print(f"Postoupil jsi na pole {herniDeska[player.pozice].nazev} na pozici {player.pozice}.")
            elif "distancbez4000" in karta:
                # posunout hrace na distanc (je jen jeden)
                for i in range(len(herniDeska)):
                    if herniDeska[i].typ == "distanc":
                        player.pozice = i
                        print(f"Postoupil jsi na pole {herniDeska[player.pozice].nazev} na pozici {player.pozice}.")
                        break
            elif "zpetnapoli4000" in karta:
                for pole in herniDeska:
                    if pole.typ == "kun" and pole.druh == "Napoli":
                        poziceNapoli = herniDeska.index(pole)
                        break
                # 4k obrdzi i kdyz nepresel start
                player.penize += 4000
                player.pozice = poziceNapoli
                print(f"Vracíš se na pole {herniDeska[player.pozice].nazev} na pozici {player.pozice} a získáváš 4.000 peněz.")
                # opět je potřeba projet funkci koupeni znova le to pak (WIP, dodelat pak)
            elif "zpetdistanc" in karta:
                # najit distanc
                for i in range(len(herniDeska)):
                    if herniDeska[i].typ == "distanc":
                        poziceDistanc = i
                        break
                # check jestli presel start
                if poziceDistanc > player.pozice: # presel start
                    player.penize += 4000 # dostane 4000
                    print("Prošel jsi Startem a získal 4.000 peněz!")
                player.pozice = poziceDistanc
                print(f"Vracíš se na pole {herniDeska[player.pozice].nazev} na pozici {player.pozice}.")
            elif "finance" in karta:
                # najit nejblizsi finance pole
                nejblizsiFinancePozice = None
                for i in range(1, len(herniDeska)): # projit vsechna pole
                    poziceCheck = (player.pozice + i) % len(herniDeska) # pozice ktera se kontroluje
                    if herniDeska[poziceCheck].typ == "finance": # jestli je to finance
                        nejblizsiFinancePozice = poziceCheck
                        break # nasel jsme nejblizsi finance
                if nejblizsiFinancePozice is not None: # nasel jsme nejblizsi finance
                    player.pozice = nejblizsiFinancePozice
                    print(f"Postoupil jsi na pole {herniDeska[player.pozice].nazev} na pozici {player.pozice}.")
                    # spusit nahodne finance (WIP, dodelat pak)                    
            elif "start4000" in karta:
                player.pozice = 0
                player.penize += 4000
                print("Vracíš se na Start a získáváš 4.000.")
            elif "startbez4000" in karta:
                player.pozice = 0
                print("Vracíš se na Start (bez 4000).")
            elif "pauza2" in karta:
                player.kolikKolNehraje = 2
                print("Zdržíš se na 2 kola.")
            elif "pauza1" in karta:
                player.kolikKolNehraje = 1
                print("Zdržíš se na 1 kolo.")
            elif "zpetparkoviste" in karta:
                # najit parkoviste
                for i in range(len(herniDeska)):
                    if herniDeska[i].typ == "parkoviste":
                        poziceParkoviste = i
                        break
                # check jestli presel start
                if poziceParkoviste > player.pozice: # presel start
                    player.penize += 4000 # dostane 4000
                    print("Prošel jsi Startem a získal 4.000 peněz!")
                player.pozice = poziceParkoviste
                print(f"Vracíš se na pole {herniDeska[player.pozice].nazev} na pozici {player.pozice}.")
        # ==================
        # POLE TYPU VETERINA
        # ==================       
        elif aktualniPole.typ == "veterina": # veterina
            print(f"Musíš zaplatit veterinární ošetření ve výši {aktualniPole.platba} peněz.")
            if player.penize >= aktualniPole.platba: # ma dost penez?
                player.penize -= aktualniPole.platba # ano
                print(f"Zaplatil jsi {aktualniPole.platba} peněz za veterinární ošetření.")
            else: # nema dost penez
                print("Nemáš dost peněz na zaplacení veterinárního ošetření!")
                bankrot()
        # ================
        # POLE TYPU TRENER
        # ================
        elif aktualniPole.typ == "trener": # pole typu trener
            if aktualniPole.vlastnik is None: # a neni nikym vlastneny
                print(f"{aktualniPole.nazev} stojí {aktualniPole.cena} peněz.")
                if not player.jeAI:
                    koupit = input("Chceš si ho koupit? (a/n): ")
                else:
                    trenerKoupitMsg = f"Jsi na poli s trenérem č.{aktualniPole.cisloTrenera} který stojí {aktualniPole.cena} peněz a nemá vlastníka. Máš {player.penize} peněz. Chceš si tohoto trenéra koupit? Odpověž pouze 'a' pro ano nebo 'n' pro ne."
                    aiResponse = queryAI(trenerKoupitMsg)
                    koupit = aiResponse.message.content.strip().lower()
                    print(f"AI odpověděla: {koupit} (s myšlením: {aiResponse.message.thinking})")
                if koupit.lower() == "a": # hrac se ho rozhodl koupit
                    if player.penize >= aktualniPole.cena: # ma dost penez?
                        player.penize -= aktualniPole.cena # odecist penize
                        aktualniPole.vlastnik = player.cisloHrace # nastavit vlastnika
                        print(f"Koupil jsi trenéra č.{aktualniPole.cisloTrenera}!")
                    else: # nema dost penez...
                        print("Nemáš dost peněz na koupi tohoto trenéra.")
                else: # nechce
                    print("Rozhodl jsi se trenéra nekoupit.")
            else: # uz ma vlastnika
                if aktualniPole.vlastnik == player.cisloHrace: # je to trener aktualniho hrace
                    print("Tento trenér patří tobě.")
                else: # neni to trener aktualniho hrace
                    # vypocitat kolik treneru vlastni vlastnik tohohle
                    pocetTreneruVlastnik = 0
                    poplatek = 0
                    for pole in herniDeska: # projit vsechny pole
                        if pole.typ == "trener" and pole.vlastnik == aktualniPole.vlastnik: # pokud je to trener a vlastnik je stejny
                            pocetTreneruVlastnik += 1 # pricist
                    # vypocitat poplatek (1000 za kazdeho trenera)
                    poplatek = pocetTreneruVlastnik * 1000
                    print(f"Tento trenér patří hráči {aktualniPole.vlastnik}. Hráč {aktualniPole.vlastnik} vlastní {pocetTreneruVlastnik} z {pocetTreneruNaDesce}. Musíš mu zaplatit poplatek {poplatek} peněz.")
                    if not player.jeAI:
                        input("Stiskni Enter pro zaplacení poplatku...")
                    else:
                        # Není potřeba dávat query na AI protože to je jen platba
                        pass
                    if player.penize >= poplatek: # má dost peněz na poplatek
                        player.penize -= poplatek # odčíst peníze
                        for hracVlastnik in hraci: # najit vlastnika a prict penize
                            if hracVlastnik.cisloHrace == aktualniPole.vlastnik:
                                hracVlastnik.penize += poplatek
                                print(f"Zaplatil jsi {poplatek} peněz hráči {hracVlastnik.jmeno}.")
                                break
                    else:
                        print("Nemáš dost peněz na zaplacení poplatku!")
                        bankrot()
        # ==================
        # POLE TYPU PREPRAVA
        # ==================
        elif aktualniPole.typ == "preprava": # pole typu preprava
            if aktualniPole.vlastnik is None: # a neni nikym vlastneny
                print(f"{aktualniPole.nazev} stojí {aktualniPole.cena} peněz.")
                if not player.jeAI:
                    koupit = input("Chceš si jej koupit? (a/n): ")
                else:
                    koupitPrepravuMsg = f"Jsi na poli s přepravou {aktualniPole.nazev} která stojí {aktualniPole.cena} peněz a nemá vlastníka. Máš {player.penize} peněz. Chceš si tuto přepravu koupit? Odpověž pouze 'a' pro ano nebo 'n' pro ne."
                    aiResponse = queryAI(koupitPrepravuMsg)
                    koupit = aiResponse.message.content.strip().lower()
                    print(f"AI odpověděla: {koupit} (s myšlením: {aiResponse.message.thinking})")
                if koupit.lower() == "a": # hrac se ho rozhodl koupit
                    if player.penize >= aktualniPole.cena: # ma dost penez?
                        player.penize -= aktualniPole.cena # odecist penize
                        aktualniPole.vlastnik = player.cisloHrace # nastavit vlastnika
                        print(f"Koupil jsi {aktualniPole.nazev}!")
                    else: # nema dost penez...
                        print(f"Nemáš dost peněz na koupi {aktualniPole.nazev}.")
                else: # nechce
                    print(f"Rozhodl jsi se {aktualniPole.nazev} nekoupit.")
                
            else: # uz ma vlastnika
                if aktualniPole.vlastnik == player.cisloHrace: # je to preprava aktualniho hrace
                    print(f"{aktualniPole.nazev} patří tobě.")
                else: # neni to preprava aktualniho hrace
                    poplatekBase = 80 # pevny poplatek za prepravu
                    # ma vlastnik i staje?
                    vlastnikMaStaje = False
                    for pole in herniDeska:
                        if pole.typ == "staje" and pole.vlastnik == aktualniPole.vlastnik:
                            vlastnikMaStaje = True
                            break
                    # vypocitat poplatek
                    if vlastnikMaStaje:
                        poplatek = 360 # pokud ma staje, tak vetsi poplatek
                    else:
                        poplatek = poplatekBase
                    # hod kostkou pro urceni poplatku
                    if not player.jeAI:
                        input("Stiskni Enter pro hod kostkou pro určení poplatku přepravy...")
                    else:
                        # Není potřeba dávat query na AI protože to je jen hod kostkou
                        pass
                    hodPreprava = random.randint(1, 6)
                    print(f"Hodil jsi {hodPreprava} pro určení poplatku přepravy.")
                    poplatek *= hodPreprava                    
                    print(f"Toto přepravní pole patří hráči {aktualniPole.vlastnik}. Musíš mu zaplatit poplatek {poplatek} peněz.")
                    if not player.jeAI:
                        input("Stiskni Enter pro zaplacení poplatku...")
                    else:
                        # Není potřeba dávat query na AI protože to je jen platba
                        pass
                    if player.penize >= poplatek: # má dost peněz na poplatek
                        player.penize -= poplatek # odčíst peníze
                        for hracVlastnik in hraci: # najit vlastnika a prict penize
                            if hracVlastnik.cisloHrace == aktualniPole.vlastnik:
                                hracVlastnik.penize += poplatek
                                print(f"Zaplatil jsi {poplatek} peněz hráči {hracVlastnik.jmeno}.")
                                break
                    else:
                        print("Nemáš dost peněz na zaplacení poplatku!")
                        bankrot()
        # ===============
        # POLE TYPU STAJE
        # ===============
        elif aktualniPole.typ == "staje": # pole typu staje
            if aktualniPole.vlastnik is None: # a neni nikym vlastneny
                print(f"{aktualniPole.nazev} stojí {aktualniPole.cena} peněz.")
                if not player.jeAI:
                    koupit = input("Chceš si je koupit? (a/n): ")
                else:
                    # Není potřeba dávat query na AI protože to je jen rozhodnutí
                    pass
                if koupit.lower() == "a": # hrac se ho rozhodl koupit
                    if player.penize >= aktualniPole.cena: # ma dost penez?
                        player.penize -= aktualniPole.cena # odecist penize
                        aktualniPole.vlastnik = player.cisloHrace # nastavit vlastnika
                        print(f"Koupil jsi {aktualniPole.nazev}!")
                    else: # nema dost penez...
                        print(f"Nemáš dost peněz na koupi {aktualniPole.nazev}.")
                else: # nechce
                    print(f"Rozhodl jsi se {aktualniPole.nazev} nekoupit.")
            else: # uz ma vlastnika
                if aktualniPole.vlastnik == player.cisloHrace: # jsou to staje aktualniho hrace
                    print(f"{aktualniPole.nazev} patří tobě.")
                else: # neni to preprava aktualniho hrace
                    poplatekBase = 80 # pevny poplatek za prepravu
                    # ma vlastnik i staje?
                    vlastnikMaPrepravu = False
                    for pole in herniDeska:
                        if pole.typ == "preprava" and pole.vlastnik == aktualniPole.vlastnik:
                            vlastnikMaPrepravu = True
                            break
                    # vypocitat poplatek
                    if vlastnikMaPrepravu:
                        poplatek = 360 # pokud ma staje, tak vetsi poplatek
                    else:
                        poplatek = poplatekBase
                    # hod kostkou pro urceni poplatku
                    if not player.jeAI:
                        input("Stiskni Enter pro hod kostkou pro určení poplatku stájí...")
                    else:
                        # Není potřeba dávat query na AI protože to je jen hod kostkou
                        pass
                    hodStaje = random.randint(1, 6)
                    print(f"Hodil jsi {hodStaje} pro určení poplatku stájí.")
                    poplatek *= hodStaje                    
                    print(f"Toto pole patří hráči {aktualniPole.vlastnik}. Musíš mu zaplatit poplatek {poplatek} peněz.")
                    if not player.jeAI:
                        input("Stiskni Enter pro zaplacení poplatku...")
                    else:
                        # Není potřeba dávat query na AI protože to je jen platba
                        pass
                    if player.penize >= poplatek: # má dost peněz na poplatek
                        player.penize -= poplatek # odčíst peníze
                        for hracVlastnik in hraci: # najit vlastnika a prict penize
                            if hracVlastnik.cisloHrace == aktualniPole.vlastnik:
                                hracVlastnik.penize += poplatek
                                print(f"Zaplatil jsi {poplatek} peněz hráči {hracVlastnik.jmeno}.")
                                break
                    else:
                        print("Nemáš dost peněz na zaplacení poplatku!")
                        bankrot()
        # ================
        # POLE TYPU DOPING
        # ================
        elif aktualniPole.typ == "doping": # doping
            # pricist +1 kolik kol nehraje
            player.kolikKolNehraje += 1
            print("Dostal jsi dopingovou pauzu! Zdržíš se o 1 kolo.")
        

        # jsem na distancu?
        if herniDeska[player.pozice].typ == "distanc":
            player.jeNaDistancu = True
        else:
            player.jeNaDistancu = False
        
        # DEBUG - BUDE ODSTRANENO
        input("Stiskni Enter pro pokračování na dalšího hráče...")
    