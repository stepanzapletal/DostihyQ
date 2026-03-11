<p align="center">
  <h1 align="center">🐎 DostihyQ</h1>

  <p align="center">
    Digitální verze deskové hry <i>Dostihy a sázky</i> v Pythonu.<br>
    Nabízí grafické rozhraní a lokálního AI soupeře poháněného <b>Ollama</b>.
  </p>

  <p align="center">
    <a href="README.md">
      <img src="https://img.shields.io/badge/English-README.md-blue?style=for-the-badge">
    </a>
  </p>
</p>

---

# Instalace

Pro spuštění hry potřebujete **Python** a **Ollamu** nainstalované ve vašem systému.

## 1. Instalace Ollamy
Stáhněte a nainstalujte Ollamu z oficiálních stránek.

## 2. Spuštění Ollama serveru

Otevřete terminál a spusťte:

```bash
ollama serve
```

## 3. Stažení AI modelu

Otevřete **nové okno terminálu** a spusťte:

```bash
ollama run gemma3n:e4b
```

## 4. Instalace Python balíčků

```bash
pip install customtkinter ollama
```

---

# Spouštění

Před spuštěním hry je **VELMI doporučeno** otestovat, zda-li AI komunikuje správně.

## 1. Test spojení s AI

Spusťte testovací skript:

```bash
python ollamaTEST.py
```

Pokud vše funguje, měli byste obdržet ukázkovou odpověď od modelu **Gemma**.

---

## 2. Spuštění hry

Hru lze spustit buď přes **GUI verzi**, nebo přes velmi zastaralou **terminálovou verzi**.

### GUI verze (doporučeno)

```bash
python GUIVerze.py
```

### Terminálová verze (pouze pro testování)

```bash
python konzolovaVerze.py
```

---

# FAQ

## Proč nepoužít online API pro lepší výkon?

Místo externího API, které by vyžadovalo výběr poskytovatele a řešení možných problémů s připojením, projekt využívá **lokální AI**.

Tento přístup má sice své výhody, ale také nevýhody:

- Horší výkon na systémech bez GPU
- Občasné problémy během testování

---

## Pokud je soupeř AI, byl kód také napsaný AI?

Ne.

AI byla v projektu využita pouze jednou a to pro ladění chyby, kterou jsem udělal v prioritě argumentů, což způsobilo nesprávnou podmínku if.

Projekt původně začal jako **terminálová verze**, kterou jsem napsal jako "tech demo". Tato verze nyní není udržovaná a je zastaralá. Později byla hra přepsána do **GUI verze**, která je finálním produktem.

Můžete si všimnout neobvyklého formátování v kódu, což je způsobeno:

- Vývojem na **Linuxu**
- Občasným rozhozením formátování ve **VS Code** (nějak mi to zlobilo)
- Použitím **Black** formátovače pro přeformátování kódu (rozbalení parametrů na více řádků atd...)
- Mým zvykem komentovat téměř každý řádek

I když kód může někdy působit jako AI-generovaný, je kompletně napsaný ručně.

---

## Proč použít textový AI model místo trénování neuronové sítě?

Toto rozhodnutí bylo motivováno **strukturou původní konzolové verze**.

Trénování neuronové sítě by pravděpodobně vyžadovalo kompletní přepis kódu. Místo toho jsem zvolil **textový model**, který dokáže pracovat s existující logikou hry.

Testoval jsem několik modelů (cca 8) pomocí jednoduchých benchmarků. Každý kandidát musel splňovat:

- Lehkost a snadné spuštění lokálně  
- Malou velikost a efektivitu  
- Vyšší spolehlivost než náhodný výběr  

Nakonec jsem vybral **4B model Gemma 3n na Ollamě**.

Model by měl být schopen **základní strategie**, místo pouhého náhodného výběru, což se ukázalo jako funkční.

---

# Testování výkonu AI

Pro ověření, zda AI skutečně překonává náhodného soupeře, bylo provedeno základní testování.

Výsledky se ukázaly jako velmi úspěšné.

Model byl testován proti **čistě náhodnému soupeři** celkem **30 zápasů**.

| Výsledek | Počet | Procenta |
|------|------|------|
| Výhry | 29 | 93.55% |
| Prohry | 1 | 6.45% |
| Celkem | 30 | 100% |

Výsledkem je přibližně **93.55% úspěšnost AI**.

### Poznámky k testování

- Počet zápasů (**n = 30**) je relativně malý a statisticky nedostatečný  
- Výsledky se mohou lišit podle **systémového promptu**, protože formulace promptu ovlivňuje rozhodování modelu  
- Rozsáhlejší testy (např. 100–200 zápasů) by poskytly spolehlivější výsledky  

Protože AI běží **lokálně přes Ollamu**, každý zápas trvá znatelně dlouho. Z časových důvodů bylo použito jen omezené množství her pro tuto počáteční kontrolu.

I při malém počtu zápasů výsledky naznačují, že model je schopen rozhodování, které překonává čistě náhodný výběr.

---

# Pozorované strategické chování

Během testování se ukázalo, že AI vykazuje **základní strategické chování** místo čistě náhodného výběru.

Jedním z pozorovaných vzorců bylo, že model často **šetřil peníze místo okamžitého utrácení**, což naznačuje, že se snažil plánovat dopředu. V několika zápasech AI vynechala nepotřebné nákupy na začátku a čekala na příznivější příležitosti. Dost často se AI podařilo překročit jeho původní sumu pěnez!

Naopak **náhodný soupeř** často utrácel, kdykoli měl možnost. Jelikož jeho rozhodnutí byla čistě náhodná, často činil finančně nevýhodná rozhodnutí a rychle vyčerpal dostupné prostředky, což jej v některých případech znevýhodňovalo.

I když byl náhodný systém navržen tak, aby dělal **50/50 volby**, absence plánování znamenala, že jeho utrácení bylo agresivnější a méně udržitelné ve srovnání s opatrnějším přístupem AI.

Tento vzorec podporuje původní hypotézu, že **textový AI model může vykazovat jednoduché strategické vzorce**, pokud mu je poskytnuta strukturovaná informace o herním stavu a vhodný prompt.

Je důležité poznamenat, že tato pozorování jsou **kvalitativní a nikoli přesně měřená**, ale opakující se chování napříč několika zápasy naznačuje schopnost modelu základního plánování a rozhodování v herním prostředí.