# INFO
# Použít https://www.deskovehry.info/pravidla/dostihysazky.htm jako základ pravidel

import os
import random
import threading
import time
import customtkinter as ctk
import tkinter as tk

# AI importy
from ollama import chat
from ollama import ChatResponse

# Nastavení vzhledu
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

version = "1.2.1 MemoryMan" # id verze (nutno zmenit po zmene gitu)
programName = "DostihyQ"
preferredModel = "gemma3n:e4b"  # preferovany model (gemma top zatim)
useThinking = False
skipPost = True
requireConfirmations = True # False = AUTO | True = MANUAL
# ==========================================
# T Ř Í D Y   A   D A T A
# ==========================================
class herniPole:
    def __init__(
        self,
        typ,
        nazev,
        id,
        cena=None,
        vlastnik=None,
        odmenaZaStart=None,
        druh=None,
        platba=None,
        cisloTrenera=None,
        dostihy=None,
    ):
        self.typ = typ
        self.nazev = nazev
        self.id = id
        if typ == "start":
            self.odmenaZaStart = odmenaZaStart
        elif typ == "kun":
            self.cena = cena
            self.vlastnik = vlastnik
            self.druh = druh
            self.dostihy = dostihy
        elif typ == "finance":
            pass
        elif typ == "nahoda":
            pass
        elif typ == "veterina":
            self.platba = platba
        elif typ == "trener":
            self.cena = cena
            self.vlastnik = vlastnik
            self.cisloTrenera = cisloTrenera
        elif typ == "distanc":
            pass
        elif typ == "preprava":
            self.cena = cena
            self.vlastnik = vlastnik
        elif typ == "staje":
            self.cena = cena
            self.vlastnik = vlastnik
        elif typ == "parkoviste":
            pass
        elif typ == "doping":
            pass

    def __repr__(self):
        # Format pro tisk do AI (obnoveno z původní verze)
        params = f"typ='{self.typ}', nazev='{self.nazev}', id='{self.id}'"
        if hasattr(self, "odmenaZaStart") and self.odmenaZaStart is not None:
            params += f", odmenaZaStart={self.odmenaZaStart}"
        if hasattr(self, "cena") and self.cena is not None:
            params += f", cena={self.cena}"
        if hasattr(self, "vlastnik") and self.vlastnik is not None:
            params += f", vlastnik={repr(self.vlastnik)}"
        if hasattr(self, "druh") and self.druh is not None:
            params += f", druh='{self.druh}'"
        if hasattr(self, "dostihy") and self.dostihy is not None:
            params += f", dostihy={self.dostihy}"
        if hasattr(self, "platba") and self.platba is not None:
            params += f", platba={self.platba}"
        if hasattr(self, "cisloTrenera") and self.cisloTrenera is not None:
            params += f", cisloTrenera={self.cisloTrenera}"
        return f"herniPole({params})"


class hrac:
    def __init__(self, jmeno, cisloHrace, penize, barva, AImem, jeAI=False):
        self.jmeno = jmeno
        self.cisloHrace = cisloHrace
        self.penize = penize
        self.barva = barva
        self.jeAI = jeAI
        self.pozice = 0
        self.maKartuPrycZDistancu = False
        self.jeNaDistancu = False
        self.kolikKolNehraje = 0
        self.AImem = []


# Barvy stájí
STABLE_COLORS = {
    "Fantome": "#8B4513",
    "Gavora": "#8B4513",
    "Lady Anne": "#87CEFA",
    "Pasek": "#87CEFA",
    "Koran": "#87CEFA",
    "Neklan": "#FF69B4",
    "Portlancl": "#FF69B4",
    "Japan": "#FF69B4",
    "Kostrava": "#FFA500",
    "Lukava": "#FFA500",
    "Melák": "#FFA500",
    "Grifel": "#FF3333",
    "Mohyla": "#FF3333",
    "Metál": "#FF3333",
    "Tara": "#FFD700",
    "Furioso": "#FFD700",
    "Genius": "#FFD700",
    "Shagga": "#32CD32",
    "Dahoman": "#32CD32",
    "Gira": "#32CD32",
    "Narcius": "#4169E1",
    "Napoli": "#4169E1",
}

financeDict = {
    "platba1000": "Zaplať pojistku 1000.",
    "platba400": "Pokuta za nedodržení předpisů 400.",
    "dostihy500": "Renovuješ všechny stáje. Za každý svůj obsazený dostih zaplať 500.",
    "plus2000": "Mimořádný zisk z dostihů obdržíš 2.000.",
    "darek200": "Jako dárek k narozeninám obdržíš od každého 200.",
    "plus500": "Mimořádná prémie 500.",
    "plus4000": "Obdržíš dotaci 4.000.",
    "platba3000": "Zaplať dluh 3.000.",
    "dostihy800_2300": "Za každý svůj obsazený dostih zaplať 800, za každý hlavní dostih zaplať 2.300.",
    "platba2000": "Zaplať příspěvek 2.000.",
    "platba100": "Nákup materiálu na opravu 100.",
    "plus1000": "Výhra v loterii 1.000.",
    "plus3000": "Z banky obdržíš přeplatek 3.000.",
}

nahodyDict = {
    "zpet3": "Jdi o 3 pole zpět.",
    "bezdistancu": "Zrušen distanc (kartu lze zachovat pro pozdější použití).",
    "trenerdopredu4000": "Jedeš se zúčastnit trenérského kurzu. Postoupíš na nejbližší pole Trenér. (bez možnosti koupi)",
    "distancbez4000": "Distanc (bez 4.000).",
    "zpetnapoli4000": "Zpět na poslední pole ve hře (kůň Napoli), hráč obdrží 4.000. (bez možnosti koupi koně)",
    "zpetdistanc": "Zpět na pole Distanc.",
    "finance": "Zpět na nejbližší pole Finance. (bez jeho aktivace)",
    "start4000": "Zpět na start (hráč obdrží 4.000).",
    "startbez4000": "Zpět na start (bez 4.000).",
    "pauza2": "Zdržíš se na 2 kola.",
    "pauza1": "Zdržíš se na 1 kolo.",
    "zpetparkoviste": "Zpět na pole Parkoviště.",
}

koneDict = {
    "Fantome": {
        "koneVeStaji": ["Fantome", "Gavora"],
        "poplatek": 40,
        "platbyZaDostihy": [200, 600, 1800, 3200, 5000],
        "cenaZaDostih": 1000,
    },
    "Gavora": {
        "koneVeStaji": ["Fantome", "Gavora"],
        "poplatek": 40,
        "platbyZaDostihy": [200, 600, 1800, 3200, 5000],
        "cenaZaDostih": 1000,
    },
    "Lady Anne": {
        "koneVeStaji": ["Lady Anne", "Pasek", "Koran"],
        "poplatek": 120,
        "platbyZaDostihy": [600, 1800, 5400, 8000, 11000],
        "cenaZaDostih": 1000,
    },
    "Pasek": {
        "koneVeStaji": ["Lady Anne", "Pasek", "Koran"],
        "poplatek": 120,
        "platbyZaDostihy": [600, 1800, 5400, 8000, 11000],
        "cenaZaDostih": 1000,
    },
    "Koran": {
        "koneVeStaji": ["Lady Anne", "Pasek", "Koran"],
        "poplatek": 160,
        "platbyZaDostihy": [800, 2000, 6000, 9000, 12000],
        "cenaZaDostih": 1000,
    },
    "Neklan": {
        "koneVeStaji": ["Neklan", "Portlancl", "Japan"],
        "poplatek": 200,
        "platbyZaDostihy": [1000, 3000, 9000, 12500, 15000],
        "cenaZaDostih": 2000,
    },
    "Portlancl": {
        "koneVeStaji": ["Neklan", "Portlancl", "Japan"],
        "poplatek": 200,
        "platbyZaDostihy": [1000, 3000, 9000, 12500, 15000],
        "cenaZaDostih": 2000,
    },
    "Japan": {
        "koneVeStaji": ["Neklan", "Portlancl", "Japan"],
        "poplatek": 240,
        "platbyZaDostihy": [1200, 3600, 10000, 14000, 18000],
        "cenaZaDostih": 2000,
    },
    "Kostrava": {
        "koneVeStaji": ["Kostrava", "Lukava", "Melák"],
        "poplatek": 280,
        "platbyZaDostihy": [1400, 4000, 11000, 15000, 19000],
        "cenaZaDostih": 2000,
    },
    "Lukava": {
        "koneVeStaji": ["Kostrava", "Lukava", "Melák"],
        "poplatek": 280,
        "platbyZaDostihy": [1400, 4000, 11000, 15000, 19000],
        "cenaZaDostih": 2000,
    },
    "Melák": {
        "koneVeStaji": ["Kostrava", "Lukava", "Melák"],
        "poplatek": 320,
        "platbyZaDostihy": [1600, 4400, 12000, 16000, 20000],
        "cenaZaDostih": 2000,
    },
    "Grifel": {
        "koneVeStaji": ["Grifel", "Mohyla", "Metál"],
        "poplatek": 360,
        "platbyZaDostihy": [1800, 5000, 14000, 17000, 21000],
        "cenaZaDostih": 3000,
    },
    "Mohyla": {
        "koneVeStaji": ["Grifel", "Mohyla", "Metál"],
        "poplatek": 360,
        "platbyZaDostihy": [1800, 5000, 14000, 17000, 21000],
        "cenaZaDostih": 3000,
    },
    "Metál": {
        "koneVeStaji": ["Grifel", "Mohyla", "Metál"],
        "poplatek": 400,
        "platbyZaDostihy": [2000, 6000, 15000, 18000, 22000],
        "cenaZaDostih": 3000,
    },
    "Tara": {
        "koneVeStaji": ["Tara", "Furioso", "Genius"],
        "poplatek": 440,
        "platbyZaDostihy": [2200, 6600, 16000, 19500, 23000],
        "cenaZaDostih": 3000,
    },
    "Furioso": {
        "koneVeStaji": ["Tara", "Furioso", "Genius"],
        "poplatek": 440,
        "platbyZaDostihy": [2200, 6600, 16000, 19500, 23000],
        "cenaZaDostih": 3000,
    },
    "Genius": {
        "koneVeStaji": ["Tara", "Furioso", "Genius"],
        "poplatek": 580,
        "platbyZaDostihy": [2400, 7200, 17000, 20500, 24000],
        "cenaZaDostih": 3000,
    },
    "Shagga": {
        "koneVeStaji": ["Shagga", "Dahoman", "Gira"],
        "poplatek": 500,
        "platbyZaDostihy": [2600, 7800, 18000, 22000, 25500],
        "cenaZaDostih": 4000,
    },
    "Dahoman": {
        "koneVeStaji": ["Shagga", "Dahoman", "Gira"],
        "poplatek": 500,
        "platbyZaDostihy": [2600, 7800, 18000, 22000, 25500],
        "cenaZaDostih": 4000,
    },
    "Gira": {
        "koneVeStaji": ["Shagga", "Dahoman", "Gira"],
        "poplatek": 560,
        "platbyZaDostihy": [3000, 9000, 20000, 24000, 28000],
        "cenaZaDostih": 4000,
    },
    "Narcius": {
        "koneVeStaji": ["Narcius", "Napoli"],
        "poplatek": 700,
        "platbyZaDostihy": [3500, 10000, 22000, 26000, 30000],
        "cenaZaDostih": 4000,
    },
    "Napoli": {
        "koneVeStaji": ["Narcius", "Napoli"],
        "poplatek": 1000,
        "platbyZaDostihy": [4000, 12000, 28000, 34000, 40000],
        "cenaZaDostih": 4000,
    },
}

herniDeska = [
    herniPole("start", "Start", "start", odmenaZaStart=4000),
    herniPole("kun", "Fantome", "fantomekun", vlastnik=None, cena=1200, druh="Fantome"),
    herniPole("finance", "Finance", "finance1"),
    herniPole("kun", "Gavora", "gavorakun", vlastnik=None, cena=1200, druh="Gavora"),
    herniPole("veterina", "Veterina", "veterina1", platba=500),
    herniPole("trener", "Trenér č.1", "trener1", vlastnik=None, cena=4000, cisloTrenera=1),
    herniPole("kun", "Lady Anne", "ladyannekun", vlastnik=None, cena=2000, druh="Lady Anne"),
    herniPole("nahoda", "Náhoda", "nahoda1"),
    herniPole("kun", "Pasek", "pasekkun", vlastnik=None, cena=2000, druh="Pasek"),
    herniPole("kun", "Koran", "korankun", vlastnik=None, cena=2400, druh="Koran"),
    herniPole("distanc", "Distanc", "distanc1"),
    herniPole("kun", "Neklan", "neklankun", vlastnik=None, cena=2800, druh="Neklan"),
    herniPole("preprava", "Přeprava", "preprava", vlastnik=None, cena=3000),
    herniPole("kun", "Portlancl", "portlanclkun", vlastnik=None, cena=2800, druh="Portlancl"),
    herniPole("kun", "Japan", "japankun", vlastnik=None, cena=2800, druh="Japan"),
    herniPole("trener", "Trenér č.2", "trener2", vlastnik=None, cena=4000, cisloTrenera=2),
    herniPole("kun", "Kostrava", "kostravakun", vlastnik=None, cena=3600, druh="Kostrava"),
    herniPole("finance", "Finance", "finance2"),
    herniPole("kun", "Lukava", "lukavakun", vlastnik=None, cena=3600, druh="Lukava"),
    herniPole("kun", "Melák", "melakkun", vlastnik=None, cena=4000, druh="Melák"),
    herniPole("parkoviste", "Parkoviště", "parkoviste1"),
    herniPole("kun", "Grifel", "grifelkun", vlastnik=None, cena=4400, druh="Grifel"),
    herniPole("nahoda", "Náhoda", "nahoda2"),
    herniPole("kun", "Mohyla", "mohylakun", vlastnik=None, cena=4400, druh="Mohyla"),
    herniPole("kun", "Metál", "metalkun", vlastnik=None, cena=4800, druh="Metál"),
    herniPole("trener", "Trenér č.3", "trener3", vlastnik=None, cena=4000, cisloTrenera=3),
    herniPole("kun", "Tara", "tarakun", vlastnik=None, cena=5200, druh="Tara"),
    herniPole("kun", "Furioso", "furiosokun", vlastnik=None, cena=5200, druh="Furioso"),
    herniPole("staje", "Stáje", "staje1", vlastnik=None, cena=3000),
    herniPole("kun", "Genius", "geniuskun", vlastnik=None, cena=5600, druh="Genius"),
    herniPole("doping", "Doping", "doping1"),
    herniPole("kun", "Shagga", "shaggakun", vlastnik=None, cena=6000, druh="Shagga"),
    herniPole("kun", "Dahoman", "dahomankun", vlastnik=None, cena=6000, druh="Dahoman"),
    herniPole("finance", "Finance", "finance3"),
    herniPole("kun", "Gira", "girakun", vlastnik=None, cena=6400, druh="Gira"),
    herniPole("trener", "Trenér č.4", "trener4", vlastnik=None, cena=4000, cisloTrenera=4),
    herniPole("nahoda", "Náhoda", "nahoda3"),
    herniPole("kun", "Narcius", "narcius", vlastnik=None, cena=7000, druh="Narcius"),
    herniPole("veterina", "Veterina", "veterina2", platba=1000),
    herniPole("kun", "Napoli", "napoli", vlastnik=None, cena=8000, druh="Napoli"),
]

# --- REDUNDANCY CHECKS ---
for pole in herniDeska:
    if pole.typ == "kun" and pole.druh not in koneDict:
        print(f"Chyba: Kůň {pole.druh} na poli {pole.nazev} není v koneDict!")
        exit()

pocetPreprav = sum(1 for p in herniDeska if p.typ == "preprava")
pocetStaji = sum(1 for p in herniDeska if p.typ == "staje")
if pocetPreprav > 1 or pocetStaji > 1:
    print("Chyba: Na herní desce je více než jedno pole přepravy nebo stájí!")
    exit()

pocetHracu = 2
pocetTreneruNaDesce = max([p.cisloTrenera for p in herniDeska if p.typ == "trener"])
pocetZacatecnichPenez = 30000
hraci = [ # pozor na definice aby se nepriradily k spatnymu
    hrac("Hráč 1 (Vy)", 1, pocetZacatecnichPenez, "#3498db", AImem=[], jeAI=False),
    hrac("Počítač (AI)", 2, pocetZacatecnichPenez, "#e74c3c", AImem=[], jeAI=True),
]
print(hraci[0].AImem) # test
# Sestavení původního layoutu pro AI
layoutDesky = ""
for pole in herniDeska:
    layoutDesky += repr(pole) + "\n"

systemPromptBehavior = f"""You are an assistant for the board a game called "Dostihy a sázky" (Czech Horse Racing and Betting). Your purpose is to win the game at all costs.
You will be playing against human players. You must make decisions based on the current game state and your strategy to win.
Below is the default configuration of the game board (this will NOT change):
{layoutDesky}

Also, here is the dictionary of horses and their attributes:
{str(koneDict)}

You begin with {str(pocetZacatecnichPenez)} money.
You should always form your responses very simply. Your final answers should be very simple, stripped of any grammar. For example a simple a/n answer is required, or a number.
Strategize carefully and think multiple steps ahead. Make decisions that will lead you to victory.
You should prefer buying stuff rather than not, as not buying anything may disinterest the user.
I will often ask you questions to which you MUST respond with 'y'/'n' or 'ano'/'ne'. You MUST NEVER respond with grammar or reasoning."""

globalMsgHistory = [{"role": "system", "content": systemPromptBehavior}] # GLOBALNI, NEMENIT!!!!
for iHrac in hraci:
    if iHrac.jeAI: # pouze AI hrace
        iHrac.AImem = [{"role": "system", "content": systemPromptBehavior}]
    else:
        print("Hráč není AI, pokračuji bez paměti")

falesnyHrac = hrac("FAKE", 0, 0, "#000000", AImem=globalMsgHistory, jeAI=False)

def queryAI(currentPlayer, userprompt, set_status, isMsgTemporary=False):
    playerMemory = currentPlayer.AImem
    if not isMsgTemporary:
        playerMemory.append({"role": "user", "content": userprompt})
    try:
        set_status("🤖 AI přemýšlí...")
        response: ChatResponse = chat(model=preferredModel, messages=playerMemory, think=useThinking)
        set_status("🤖 AI zahrála.")
        print("AI Response: \n" + str(response))
        # ULOŽIT ODPOVĚĎ!
        if not isMsgTemporary:
            playerMemory.append({"role": "assistant", "content": response.message.content})

        return response
    except Exception as e:
        print("CHYBA v zpracování AI!!!!! Používám fallback s thinkingem exceptionu...")
        print(str(e))
        return type( # fallback
            "obj",
            (object,),
            {"message": type("obj", (object,), {"content": "a", "thinking": str(e)})},
        )()
        
def randomYN():
    randomChoice = random.choice(["a", "n"])
    print("RC: "+randomChoice)
    return randomChoice

# funkce brainwashingu - clearnuti pameti
def brainwashAI():
    for hrac_ in hraci:
        if hrac_.jeAI:
            # tvortba noveho listu (pozor at se to shoduje)
            hrac_.AImem = [{"role": "system", "content": systemPromptBehavior}]

# ==========================================
# G U I   A   H E R N Í   D E S K A
# ==========================================
class QwostihyGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"{programName} - {version}")
        self.geometry("1300x850")

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.user_input = None
        self.input_event = threading.Event()
        self.game_thread = None
        self.cell_size = 70
        self.tooltip = None

        self.setup_ui()
        self.update_board_visuals()

    def setup_ui(self):
        self.board_frame = ctk.CTkFrame(self, fg_color="#1e1e1e", corner_radius=15)
        self.board_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        self.canvas = tk.Canvas(self.board_frame, bg="#1e1e1e", highlightthickness=0)
        self.canvas.pack(expand=True, fill="both", padx=10, pady=10)
        self.canvas.bind("<Configure>", self.on_resize)

        self.sidebar = ctk.CTkFrame(self, corner_radius=15)
        self.sidebar.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")

        self.title_label = ctk.CTkLabel(
            self.sidebar,
            text="🐴 DostihyQ",
            font=("Helvetica", 32, "bold"),
            text_color="#f39c12",
        )
        self.title_label.pack(pady=(20, 10))

        self.stats_labels = {}
        for h in hraci:
            frame = ctk.CTkFrame(
                self.sidebar,
                fg_color="#2c3e50",
                corner_radius=10,
                border_width=2,
                border_color=h.barva,
            )
            frame.pack(fill="x", padx=15, pady=8)

            lbl = ctk.CTkLabel(
                frame,
                text=f"{h.jmeno}\nPeníze: {h.penize} 💰\nPozice: {herniDeska[h.pozice].nazev}",
                font=("Arial", 14),
                justify="left",
            )
            lbl.pack(padx=10, pady=10)
            self.stats_labels[h.cisloHrace] = lbl

            frame.bind(
                "<Enter>", lambda e, h_id=h.cisloHrace: self.show_inventory(e, h_id)
            )
            frame.bind("<Leave>", self.hide_inventory)
            lbl.bind(
                "<Enter>", lambda e, h_id=h.cisloHrace: self.show_inventory(e, h_id)
            )
            lbl.bind("<Leave>", self.hide_inventory)

        self.status_label = ctk.CTkLabel(
            self.sidebar,
            text="Připravuji hru...",
            font=("Arial", 14, "italic"),
            text_color="#bdc3c7",
        )
        self.status_label.pack(pady=10)

        self.action_frame = ctk.CTkFrame(
            self.sidebar, fg_color="#1a1a1a", corner_radius=10
        )
        self.action_frame.pack(fill="both", expand=True, padx=15, pady=10)

        self.prompt_label = ctk.CTkLabel(
            self.action_frame, text="", wraplength=250, font=("Helvetica", 16, "bold")
        )
        self.prompt_label.pack(pady=20)

        self.btn_continue = ctk.CTkButton(
            self.action_frame,
            text="Pokračovat",
            command=lambda: self.submit_input(""),
            height=45,
            font=("Arial", 16, "bold"),
        )
        self.btn_yes = ctk.CTkButton(
            self.action_frame,
            text="Ano",
            fg_color="#27ae60",
            hover_color="#2ecc71",
            command=lambda: self.submit_input("a"),
            height=45,
        )
        self.btn_no = ctk.CTkButton(
            self.action_frame,
            text="Ne",
            fg_color="#c0392b",
            hover_color="#e74c3c",
            command=lambda: self.submit_input("n"),
            height=45,
        )
        self.text_entry = ctk.CTkEntry(
            self.action_frame, placeholder_text="Zadej...", height=40
        )
        self.btn_submit = ctk.CTkButton(
            self.action_frame,
            text="Potvrdit",
            command=lambda: self.submit_input(self.text_entry.get()),
            height=40,
        )

        self.log_box = ctk.CTkTextbox(
            self.sidebar,
            height=350,
            font=("Consolas", 12),
            fg_color="#111",
            corner_radius=10,
        )
        self.log_box.pack(fill="x", padx=15, pady=(0, 15), side="bottom")

    def show_inventory(self, event, hrac_id):
        if self.tooltip:
            self.hide_inventory(None)
        vlastneno = [
            p.nazev for p in herniDeska if getattr(p, "vlastnik", -1) == hrac_id
        ]
        text_inv = (
            "Žádný majetek"
            if not vlastneno
            else "Vlastněno:\n" + "\n".join(f"• {k}" for k in vlastneno)
        )

        self.tooltip = tk.Toplevel(self)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.configure(bg="#34495e")
        x, y = self.winfo_pointerx() + 15, self.winfo_pointery() + 15
        self.tooltip.geometry(f"+{x}+{y}")

        lbl = tk.Label(
            self.tooltip,
            text=text_inv,
            bg="#34495e",
            fg="white",
            font=("Arial", 12),
            justify="left",
            padx=10,
            pady=10,
        )
        lbl.pack()

    def hide_inventory(self, event):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

    def on_resize(self, event):
        velikost = min(event.width, event.height) // 11
        if velikost != self.cell_size and velikost > 20:
            self.cell_size = velikost
            self.update_board_visuals()

    def get_coords(self, index):
        if 0 <= index <= 10:
            x, y = 10 - index, 10
        elif 11 <= index <= 20:
            x, y = 0, 10 - (index - 10)
        elif 21 <= index <= 30:
            x, y = index - 20, 0
        else:
            x, y = 10, index - 30

        offset_x = max(0, (self.canvas.winfo_width() - (self.cell_size * 11)) / 2)
        offset_y = max(0, (self.canvas.winfo_height() - (self.cell_size * 11)) / 2)
        return offset_x + (x * self.cell_size), offset_y + (y * self.cell_size)

    def draw_board_grid(self):
        self.canvas.delete("all")
        for i, pole in enumerate(herniDeska):
            x, y = self.get_coords(i)
            cs = self.cell_size

            bg_color = "#bdc3c7"
            if pole.typ in [
                "start",
                "finance",
                "nahoda",
                "distanc",
                "parkoviste",
                "doping",
            ]:
                if pole.typ == "start":
                    bg_color = "#f1c40f"
                elif pole.typ == "finance":
                    bg_color = "#2ecc71"
                elif pole.typ == "nahoda":
                    bg_color = "#3498db"
                else:
                    bg_color = "#e74c3c"

            self.canvas.create_rectangle(
                x, y, x + cs, y + cs, fill=bg_color, outline="#2c3e50", width=2
            )

            if pole.typ == "kun":
                header_color = STABLE_COLORS.get(pole.druh, "#333333")
                self.canvas.create_rectangle(
                    x, y, x + cs, y + (cs * 0.3), fill=header_color, outline="#2c3e50"
                )
            elif pole.typ in ["trener", "preprava", "staje"]:
                self.canvas.create_rectangle(
                    x, y, x + cs, y + (cs * 0.3), fill="#7f8c8d", outline="#2c3e50"
                )

            font_size = max(8, int(cs * 0.12))
            text = (
                pole.nazev.split(" ")[0][:9]
                if "Kůň" not in pole.nazev
                else pole.nazev.replace("Kůň ", "")[:9]
            )
            self.canvas.create_text(
                x + cs / 2,
                y + cs * 0.5,
                text=text,
                font=("Arial", font_size, "bold"),
                fill="#222",
            )

            if hasattr(pole, "cena") and pole.cena:
                self.canvas.create_text(
                    x + cs / 2,
                    y + cs * 0.8,
                    text=f"{pole.cena} $",
                    font=("Arial", font_size - 1),
                    fill="#444",
                )

    def update_board_visuals(self):
        self.draw_board_grid()
        cs = self.cell_size

        for i, pole in enumerate(herniDeska):
            if hasattr(pole, "vlastnik") and pole.vlastnik is not None:
                x, y = self.get_coords(i)
                barva_vlastnika = hraci[pole.vlastnik - 1].barva
                self.canvas.create_rectangle(
                    x,
                    y + cs - (cs * 0.15),
                    x + cs,
                    y + cs,
                    fill=barva_vlastnika,
                    outline="",
                    tags="dynamic",
                )

        for idx, h in enumerate(hraci):
            x, y = self.get_coords(h.pozice)
            r = max(4, int(cs * 0.15))
            offset_x = (cs * 0.3) if idx == 0 else (cs * 0.7)
            offset_y = cs * 0.7
            cx, cy = x + offset_x, y + offset_y
            self.canvas.create_oval(
                cx - r,
                cy - r,
                cx + r,
                cy + r,
                fill=h.barva,
                outline="white",
                width=2,
                tags="dynamic",
            )

        for h in hraci:
            self.stats_labels[h.cisloHrace].configure(
                text=f"{h.jmeno}\nPeníze: {h.penize} 💰\nPozice: {herniDeska[h.pozice].nazev}"
            )

    def set_status(self, text):
        self.after(0, lambda: self.status_label.configure(text=text))

    def syslog(self, text):
        def append():
            self.log_box.insert("end", text + "\n")
            self.log_box.see("end")

        self.after(0, append)

    def submit_input(self, value):
        self.user_input = value
        self.input_event.set()

    def wait_for_input(self, prompt_text, input_type="continue"):
        global requireConfirmations
        # --- AUTO MOD ---
        if not requireConfirmations:
            # vypsat prompttext
            self.after(0, lambda: self.prompt_label.configure(text=prompt_text))
            
            # pauza
            #time.sleep(0.5) 
            
            # simulace kliků
            if input_type == "continue":
                return ""   # continue
            elif input_type == "yesno":
                return randomYN()  # y/n random
            elif input_type == "text":
                randomInt = random.randint(1,4)
                return randomInt  # nemelo by jet dyz mam random mode
        # -------------------------------------------------------
        def setup():
            self.prompt_label.configure(text=prompt_text)
            self.btn_continue.pack_forget()
            self.btn_yes.pack_forget()
            self.btn_no.pack_forget()
            self.text_entry.pack_forget()
            self.btn_submit.pack_forget()

            if input_type == "continue":
                self.btn_continue.pack(pady=10)
            elif input_type == "yesno":
                self.btn_yes.pack(pady=5, fill="x")
                self.btn_no.pack(pady=5, fill="x")
            elif input_type == "text":
                self.text_entry.delete(0, "end")
                self.text_entry.pack(pady=5)
                self.btn_submit.pack(pady=5, fill="x")

        self.after(0, setup)
        self.input_event.clear()
        self.input_event.wait()

        self.after(0, lambda: self.prompt_label.configure(text="Zpracovávám..."))
        self.after(0, self.btn_continue.pack_forget)
        self.after(0, self.btn_yes.pack_forget)
        self.after(0, self.btn_no.pack_forget)
        return self.user_input

    def start_game_thread(self):
        self.game_thread = threading.Thread(
            target=run_game_logic, args=(self,), daemon=True
        )
        self.game_thread.start()


# ==========================================
# H E R N Í   L O G I K A   (Vlákno)
# ==========================================
def run_game_logic(app: QwostihyGUI):
    def bankrot(hrac_jmeno):
        app.syslog(f"❌ {hrac_jmeno} je v bankrotu! Konec hry.")
        app.wait_for_input("Hra skončila. Zavři okno.", "continue")
        input("Stiskni Enter pro ukončení hry\n>>>  ")
        os._exit(0)

    app.syslog("AI startuje (může trvat až minutu)...")
    if not skipPost:
        while True:
            q = queryAI(
                falesnyHrac,
                "Simply respond to this message with 'ano' and nothing else",
                app.set_status,
                True,
            )
            if "ano" or "y" in q.message.content.strip().lower():
                break
            else:
                brainwashAI() # vyčistit pamět
                print("Init failed! AI Brainwashed")
                app.syslog("AI POST selhal, zkouším znovu...")
    app.syslog("AI ready!")
    app.set_status("Hra běží")

    while True:
        for player in hraci:
            app.wait_for_input(f"Tah: {player.jmeno}", "continue")

            tempNeniNaDistancu = False
            if player.kolikKolNehraje > 0:
                app.syslog(
                    f"⏸️ {player.jmeno} se zdrží o {player.kolikKolNehraje} kola."
                )
                player.kolikKolNehraje -= 1
                app.after(0, app.update_board_visuals)
                continue

            app.set_status(f"Hraje {player.jmeno}")

            if (
                herniDeska[player.pozice].typ == "distanc"
                and player.maKartuPrycZDistancu
            ):
                if not player.jeAI:
                    chce = app.wait_for_input(
                        "Jsi na distancu. Použít kartu zrušení?", "yesno"
                    )
                else:
                    chce = (
                        queryAI(
                            player,
                            "Jsi na distancu. Použít propustku? (a/n)", app.set_status
                        )
                        .message.content.strip()
                        .lower()
                    )
                if chce in ["a", "ano"]:
                    player.maKartuPrycZDistancu = False
                    tempNeniNaDistancu = True
                    app.syslog("Použita karta zrušení distancu.")

            if not player.jeAI:
                app.wait_for_input("Tvůj tah! Hoď kostkou.", "continue")
            else:
                time.sleep(0.5)

            hod = random.randint(1, 6)
            app.syslog(f"🎲 {player.jmeno} hodil {hod}.")

            if (
                hod == 6
                and not tempNeniNaDistancu
                and herniDeska[player.pozice].typ == "distanc"
            ):
                app.syslog("Šestka na distancu! Házíš znovu.")
                if not player.jeAI:
                    app.wait_for_input("Hoď znovu", "continue")
                hod = random.randint(1, 6)
            elif herniDeska[player.pozice].typ == "distanc" and not tempNeniNaDistancu:
                app.syslog("Nehodil jsi 6. Zůstáváš na distancu.")
                continue

            if hod == 6 and herniDeska[player.pozice].typ != "distanc":
                if not player.jeAI:
                    app.wait_for_input("Hodil jsi 6! Házíš dál.", "continue")
                else:
                    time.sleep(0.5)
                dalsi = random.randint(1, 6)
                app.syslog(f"Druhý hod: {dalsi}")
                hod += dalsi
                if hod == 12:
                    app.syslog("Dvě šestky! Jdeš rovnou na distanc.")
                    player.pozice = next(
                        i for i, p in enumerate(herniDeska) if p.typ == "distanc"
                    )
                    app.after(0, app.update_board_visuals)
                    continue

            # Posun na desce
            for step in range(hod):
                player.pozice += 1
                if player.pozice >= len(herniDeska):
                    player.pozice = 0
                    player.penize += herniDeska[0].odmenaZaStart
                    app.syslog(
                        f"🏁 Prošel jsi Startem! Zisk: {herniDeska[0].odmenaZaStart}"
                    )
                app.after(0, app.update_board_visuals)
                time.sleep(0.1)

            aktualniPole = herniDeska[player.pozice]
            app.syslog(f"📍 Stojíš na: {aktualniPole.nazev}")

            # =================
            # POLE TYPU KŮŇ
            # =================
            if aktualniPole.typ == "kun":
                if aktualniPole.vlastnik is None:
                    if not player.jeAI:
                        koupit = app.wait_for_input(
                            f"Koupit {aktualniPole.nazev} za {aktualniPole.cena}?",
                            "yesno",
                        )
                    else:
                        koupit = (
                            queryAI(
                                player,
                                f"Jsi na {aktualniPole.nazev}, stojí {aktualniPole.cena}. Máš {player.penize}. Koupit? (a/n)",
                                app.set_status,
                            )
                            .message.content.strip()
                            .lower()
                        )

                    if koupit in ["a", "ano"]:
                        if player.penize >= aktualniPole.cena:
                            player.penize -= aktualniPole.cena
                            aktualniPole.vlastnik = player.cisloHrace
                            app.syslog(f"✅ Koupil jsi {aktualniPole.nazev}")
                        else:
                            app.syslog("Nedostatek financí.")
                else:
                    if aktualniPole.vlastnik == player.cisloHrace:
                        koneVeStaji = koneDict[aktualniPole.druh]["koneVeStaji"]
                        koneCoMam = [
                            p.druh
                            for p in herniDeska
                            if p.typ == "kun" and p.vlastnik == player.cisloHrace
                        ]
                        if all(k in koneCoMam for k in koneVeStaji):
                            cd = koneDict[aktualniPole.druh]["cenaZaDostih"]
                            if aktualniPole.dostihy is None:
                                aktualniPole.dostihy = 0

                            if aktualniPole.dostihy < 4:
                                if not player.jeAI:
                                    kD = app.wait_for_input(
                                        f"Koupit dostih (cena: {cd})?", "yesno"
                                    )
                                else:
                                    kD = (
                                        queryAI(
                                            player,
                                            f"Můžeš koupit dostih za {cd}. Máš {player.penize}. Koupit? (a/n)",
                                            app.set_status,
                                        )
                                        .message.content.strip()
                                        .lower()
                                    )

                                if kD in ["a", "ano"] and player.penize >= cd:
                                    maxDostihu = 4 - aktualniPole.dostihy
                                    if not player.jeAI:
                                        pocet_in = app.wait_for_input(
                                            f"Kolik? (max {maxDostihu}):", "text"
                                        )
                                        try:
                                            pocet = int(pocet_in)
                                        except:
                                            pocet = 1
                                    else:
                                        p_ai = queryAI(
                                            player,
                                            f"Kolik dostihů? Napiš jen číslo 1 až {maxDostihu}.",
                                            app.set_status,
                                        ).message.content.strip()
                                        try:
                                            pocet = int(
                                                "".join(filter(str.isdigit, p_ai))
                                            )
                                        except:
                                            pocet = 1

                                    pocet = min(max(1, pocet), maxDostihu)
                                    if player.penize >= cd * pocet:
                                        player.penize -= cd * pocet
                                        aktualniPole.dostihy += pocet
                                        app.syslog(f"Koupeno {pocet} dostihů.")
                            elif aktualniPole.dostihy == 4:
                                if not player.jeAI:
                                    kHD = app.wait_for_input(
                                        f"Koupit Hlavní dostih ({cd})?", "yesno"
                                    )
                                else:
                                    kHD = (
                                        queryAI(
                                            player,
                                            f"Můžeš koupit hlavní dostih za {cd}. Koupit? (a/n)",
                                            app.set_status,
                                        )
                                        .message.content.strip()
                                        .lower()
                                    )
                                if kHD in ["a", "ano"] and player.penize >= cd:
                                    player.penize -= cd
                                    aktualniPole.dostihy = 5
                                    app.syslog("Koupen hlavní dostih!")
                        else:
                            app.syslog("Nemáš celou stáj, nelze kupovat dostihy.")
                    else:
                        vlastnik_hrac = hraci[aktualniPole.vlastnik - 1]
                        if aktualniPole.dostihy is None or vlastnik_hrac.jeNaDistancu:
                            poplatek = koneDict[aktualniPole.druh]["poplatek"]
                        else:
                            poplatek = koneDict[aktualniPole.druh]["platbyZaDostihy"][
                                aktualniPole.dostihy - 1
                            ]

                        app.syslog(
                            f"💸 Platíš poplatek: {poplatek} hráči {vlastnik_hrac.jmeno}"
                        )
                        if not player.jeAI:
                            app.wait_for_input("Zaplatit poplatek", "continue")
                        if player.penize >= poplatek:
                            player.penize -= poplatek
                            vlastnik_hrac.penize += poplatek
                        else:
                            bankrot(player.jmeno)

            # =================
            # POLE TYPU FINANCE
            # =================
            elif aktualniPole.typ == "finance":
                karta = random.choice(list(financeDict.keys()))
                app.syslog(f"💳 Finance: {financeDict[karta]}")

                if "platba" in karta:
                    c = int(karta.replace("platba", ""))
                    if player.penize >= c:
                        player.penize -= c
                    else:
                        bankrot(player.jmeno)
                elif "plus" in karta:
                    player.penize += int(karta.replace("plus", ""))
                elif "darek" in karta:
                    c = int(karta.replace("darek", ""))
                    total = c * (pocetHracu - 1)
                    player.penize += total
                    for oh in hraci:
                        if oh.cisloHrace != player.cisloHrace:
                            if oh.penize >= c:
                                oh.penize -= c
                            else:
                                bankrot(oh.jmeno)
                elif "dostihy" in karta:
                    c = karta.replace("dostihy", "")
                    total = 0
                    if "_" in c:
                        cd, ch = map(int, c.split("_"))
                        for p in herniDeska:
                            if p.typ == "kun" and p.vlastnik == player.cisloHrace:
                                if p.dostihy is not None and 0 < p.dostihy < 5:
                                    total += cd * p.dostihy
                                elif p.dostihy == 5:
                                    total += ch
                    else:
                        for p in herniDeska:
                            if (
                                p.typ == "kun"
                                and p.vlastnik == player.cisloHrace
                                and p.dostihy is not None
                                and 0 < p.dostihy < 5
                            ):
                                total += int(c) * p.dostihy
                    if player.penize >= total:
                        player.penize -= total
                    else:
                        bankrot(player.jmeno)

            # =================
            # POLE TYPU NÁHODA
            # =================
            elif aktualniPole.typ == "nahoda":
                karta = random.choice(list(nahodyDict.keys()))
                app.syslog(f"❓ Náhoda: {nahodyDict[karta]}")

                if "zpet3" in karta:
                    player.pozice = (player.pozice - 3) % len(herniDeska)
                elif "bezdistancu" in karta:
                    player.maKartuPrycZDistancu = True
                elif "trenerdopredu4000" in karta:
                    nt = next(
                        i
                        for i in range(1, len(herniDeska))
                        if herniDeska[(player.pozice + i) % len(herniDeska)].typ
                        == "trener"
                    )
                    target = (player.pozice + nt) % len(herniDeska)
                    if target < player.pozice:
                        player.penize += 4000
                    player.pozice = target
                elif "distancbez4000" in karta:
                    player.pozice = next(
                        i for i, p in enumerate(herniDeska) if p.typ == "distanc"
                    )
                elif "zpetnapoli4000" in karta:
                    player.penize += 4000
                    player.pozice = next(
                        i
                        for i, p in enumerate(herniDeska)
                        if p.typ == "kun" and p.druh == "Napoli"
                    )
                elif "zpetdistanc" in karta:
                    target = next(
                        i for i, p in enumerate(herniDeska) if p.typ == "distanc"
                    )
                    if target > player.pozice:
                        player.penize += 4000  # Posun dozadu přes start
                    player.pozice = target
                elif "finance" in karta:
                    nt = next(
                        i
                        for i in range(1, len(herniDeska))
                        if herniDeska[(player.pozice - i) % len(herniDeska)].typ
                        == "finance"
                    )
                    player.pozice = (player.pozice - nt) % len(herniDeska)
                elif "start4000" in karta:
                    player.pozice = 0
                    player.penize += 4000
                elif "startbez4000" in karta:
                    player.pozice = 0
                elif "pauza2" in karta:
                    player.kolikKolNehraje = 2
                elif "pauza1" in karta:
                    player.kolikKolNehraje = 1
                elif "zpetparkoviste" in karta:
                    target = next(
                        i for i, p in enumerate(herniDeska) if p.typ == "parkoviste"
                    )
                    if target > player.pozice:
                        player.penize += 4000
                    player.pozice = target

            # ==================
            # POLE TYPU VETERINA
            # ==================
            elif aktualniPole.typ == "veterina":
                app.syslog(f"🩺 Veterina: -{aktualniPole.platba}")
                player.penize -= aktualniPole.platba
                if player.penize < 0:
                    bankrot(player.jmeno)

            # ================
            # POLE TYPU TRENER
            # ================
            elif aktualniPole.typ == "trener":
                if aktualniPole.vlastnik is None:
                    if not player.jeAI:
                        k = app.wait_for_input(
                            f"Koupit trenéra za {aktualniPole.cena}?", "yesno"
                        )
                    else:
                        k = (
                            queryAI(
                                player,
                                f"Koupit trenéra za {aktualniPole.cena}? (a/n)",
                                app.set_status,
                            )
                            .message.content.strip()
                            .lower()
                        )
                    if k in ["a", "ano"] and player.penize >= aktualniPole.cena:
                        player.penize -= aktualniPole.cena
                        aktualniPole.vlastnik = player.cisloHrace
                elif aktualniPole.vlastnik != player.cisloHrace:
                    pocetVlastnenych = sum(
                        1
                        for p in herniDeska
                        if p.typ == "trener" and p.vlastnik == aktualniPole.vlastnik
                    )
                    poplatek = pocetVlastnenych * 1000
                    app.syslog(f"💸 Platíš poplatek trenéra: {poplatek}")
                    if not player.jeAI:
                        app.wait_for_input("Zaplatit poplatek", "continue")
                    if player.penize >= poplatek:
                        player.penize -= poplatek
                        hraci[aktualniPole.vlastnik - 1].penize += poplatek
                    else:
                        bankrot(player.jmeno)

            # =========================
            # POLE TYPU PREPRAVA/STAJE
            # =========================
            elif aktualniPole.typ in ["preprava", "staje"]:
                if aktualniPole.vlastnik is None:
                    if not player.jeAI:
                        k = app.wait_for_input(
                            f"Koupit {aktualniPole.nazev} za {aktualniPole.cena}?",
                            "yesno",
                        )
                    else:
                        k = (
                            queryAI(
                                player,
                                f"Koupit {aktualniPole.nazev} za {aktualniPole.cena}? (a/n)",
                                app.set_status,
                            )
                            .message.content.strip()
                            .lower()
                        )
                    if k in ["a", "ano"] and player.penize >= aktualniPole.cena:
                        player.penize -= aktualniPole.cena
                        aktualniPole.vlastnik = player.cisloHrace
                elif aktualniPole.vlastnik != player.cisloHrace:
                    druhy_typ = (
                        "staje" if aktualniPole.typ == "preprava" else "preprava"
                    )
                    maOboji = any(
                        p.typ == druhy_typ and p.vlastnik == aktualniPole.vlastnik
                        for p in herniDeska
                    )
                    zaklad = 360 if maOboji else 80

                    if not player.jeAI:
                        app.wait_for_input(
                            "Hoď kostkou pro určení poplatku", "continue"
                        )
                    hod_poplatek = random.randint(1, 6)
                    app.syslog(f"Hod pro poplatek: {hod_poplatek}")

                    poplatek = zaklad * hod_poplatek
                    app.syslog(f"💸 Platíš {aktualniPole.nazev}: {poplatek}")
                    if player.penize >= poplatek:
                        player.penize -= poplatek
                        hraci[aktualniPole.vlastnik - 1].penize += poplatek
                    else:
                        bankrot(player.jmeno)

            # ================
            # POLE TYPU DOPING
            # ================
            elif aktualniPole.typ == "doping":
                player.kolikKolNehraje += 1
                app.syslog("💉 Doping! Stojíš 1 kolo.")

            player.jeNaDistancu = (
                True if herniDeska[player.pozice].typ == "distanc" else False
            )
            app.after(0, app.update_board_visuals)


if __name__ == "__main__":
    app = QwostihyGUI()
    app.start_game_thread()
    app.mainloop()
