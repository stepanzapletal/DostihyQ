# DostihyQ
DostihyQ is a Python-based digital version of the board game "Dostihy a sázky". It features a graphical interface and allows you to play against a local AI opponent powered by Ollama.

## Installation
You need to have Python and Ollama installed on your system to run this game.

1. Install Ollama.
2. Start the Ollama server in your terminal:
###### Bash/CMD:
```ollama serve```

3. Open a new terminal window and pull/run the specific model used for the AI opponent:
###### Bash/CMD
```ollama run gemma3n:e4b```

4. Install the required Python dependencies:
###### Bash/CMD
```pip install customtkinter ollama```

## Usage
Before starting the main game, it is **highly** recommended to test your local AI setup.

1. Test the connection: Run the test script to verify that Python can communicate with your Ollama server.
###### Bash/CMD
```python ollamaTEST.py```
This should result in an example response from *gemma*

2. Run the game: You can launch the game using either the main graphical user interface (GUI) or the command-line version (which is kept primarily for testing and debugging).

3. For the GUI version, run your main file (e.g., ```python GUIVerze.py```).

(For the terminal version, run ```python konzolovaVerze.py```)
