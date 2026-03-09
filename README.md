<p align="center">
  <h1 align="center">🐎 DostihyQ</h1>

  <p align="center">
    A Python-based digital version of the board game <i>Dostihy a sázky</i><br>
    featuring a graphical interface and a local AI opponent powered by <b>Ollama</b>.
  </p>

  <p align="center">
    <a href="README_CZ.md">
      <img src="https://img.shields.io/badge/Česká%20verze-README_CZ.md-blue?style=for-the-badge">
    </a>
  </p>
</p>

---

## Installation

To run the game, you need **Python** and **Ollama** installed on your system.

## 1. Install Ollama
Download and install Ollama from its official website.

## 2. Start the Ollama server

Open a terminal and run:

```bash
ollama serve
```

## 3. Download the AI model

Open a **new terminal window** and run:

```bash
ollama run gemma3n:e4b
```

## 4. Install Python dependencies

```bash
pip install customtkinter ollama
```

---

# Usage

Before launching the game, it is **highly recommended** to test whether the AI connection works.

## 1. Test the AI connection

Run the test script:

```bash
python ollamaTEST.py
```

If everything works correctly, you should receive an example response from the **Gemma** model.

---

## 2. Run the game

You can launch either the **GUI version** or the ancient **terminal version**.

### GUI version (recommended)

```bash
python GUIVerze.py
```

### Terminal version (mainly for debugging)

```bash
python konzolovaVerze.py
```

---

# FAQ

## Why not use an online API for better performance?

Instead of using an external API, which would require choosing a provider and dealing with potential bandwidth or connection issues, the project uses a **local AI setup**.

While this avoids dependency on external services, it introduces its own drawbacks, such as:

- Poor performance on systems without GPU acceleration  
- Occasional reliability issues during testing  

---

## If the opponent is AI-powered, was the code written by AI?

No.

The project originally started as a **terminal-based prototype** that I wrote as a technical demonstration. That version is now unmaintained. Later, the game was rewritten into a **GUI-based version**, which became the final product.

You may notice some unusual formatting in the code. This is mostly because:

- I developed the project on **Linux**
- My **VS Code** formatting occasionally broke
- I ran the code through the **Black** formatter to standardize it
- I tend to leave comments on many lines of code

Because of that, the code may sometimes look similar to AI-generated output, but it is entirely written by hand.

---

## Why use a text-based AI model instead of training a neural network?

This decision was mainly due to the **structure of the original console version**.

Training a neural network would likely have required a major rewrite of the original codebase. Instead, I chose a **text-based model** that could interact with the existing game logic.

I tested several models (around eight in total) using simple benchmarks. Each candidate had to meet the following criteria:

- Lightweight and easy to run locally  
- Small and efficient  
- More reliable than random move selection  

In the end, I selected a **4B Gemma 3n model from Ollama**.

The idea was that the model should be capable of **basic strategy**, rather than making purely random moves, which turned out to work well.

---

# AI Performance Testing

Some basic testing was performed to determine whether the AI opponent actually performs better than random move selection.

The results showed very positive outcomes.

The model was tested against a **purely random opponent** for a total of **30 matches**.

| Result | Count | Percentage |
|------|------|------|
| Wins | 29 | 93.55% |
| Losses | 1 | 6.45% |
| Total | 30 | 100% |

This results in an approximate **93.55% win rate** for the AI opponent.

### Notes on testing

- The sample size (**n = 30**) is relatively small and not statistically ideal.
- Results may vary depending on the **system prompt** used, as prompt wording significantly influences the model's decision-making.
- More extensive testing (e.g., 100–200 matches) would produce more reliable results.

However, because the AI runs **locally through Ollama**, each match requires noticeable processing time. Due to these time constraints, only a limited number of games were used for this initial benchmark.

Even with the small sample size, the results suggest that the model is capable of making decisions that outperform purely random move selection.

---

# Observed Strategic Behavior

During testing, the AI appeared to demonstrate basic strategic behavior rather than making purely random decisions.

One notable pattern was that the model often **saved money instead of spending it immediately**, suggesting that it was attempting to plan ahead rather than simply choosing the first available action. In several matches, the AI avoided unnecessary purchases early in the game and appeared to wait for more favorable opportunities. At times, the AI even surpassed it's initial funds!

In contrast, the **random opponent** frequently spent money whenever possible. Because its decisions were based purely on random selection rather than strategy, it often made financially inefficient choices and depleted its available funds quickly. This behavior sometimes put the random player at a disadvantage later in the game.

Although the random decision system was designed to approximate a **50/50 choice pattern**, the lack of planning meant that its spending behavior tended to be more aggressive and less sustainable compared to the AI's more cautious approach.

This behavior supports the original hypothesis that a **text-based language model can still exhibit simple strategic patterns** when provided with structured game state information and an appropriate prompt.

It is important to note that this observation is **qualitative rather than strictly measured**, as no formal metric for “strategic play” was implemented during testing. However, the repeated appearance of these behaviors across multiple matches suggests that the model is capable of basic planning and decision-making within the game environment.