# Eagle Eyes

Eagle Eyes is a cowboy-themed, reaction-based shooting game built using Pygame. It simulates a fast-paced Western duel where players test their reflexes and timing against an opponent. The game tracks key stats like reaction time, accuracy, score, and total time played.

## Requirements

- Python 3.11.9 (recommended)  
- pip >=24.0  
- pygame >=2.6.1  
- setuptools >=65.5.0

> The game may also run on other Python 3 versions (e.g., 3.10.x or 3.12.x), but Python 3.11.9 was used during development and testing.

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/YourUsername/Eagle-Eyes.git
cd Eagle-Eyes
```

### 2. Create a virtual environment (optional but recommended)

```bash
python -m venv venv
venv\Scripts\activate   # On Windows
source venv/bin/activate # On Mac/Linux
```

### 3. Install the required packages

```bash
pip install -r requirements.txt
```

### 4. Run the game

```bash
python main.py
```

## Game Features

- Single-round duel gameplay
- Player and opponent can both shoot multiple times with reload time
- Opponent shoots randomly within a hitbox range
- Tracks player reaction time, accuracy, and duel stats
- Logs data to a `game_data.csv` file
- Animated bullets, sound effects, and hit feedback

## How to Play

- The game starts with a Western duel scenario
- Wait for the signal and shoot before the opponent
- Reload automatically after each shot (with a delay)
- Aim and shoot precisely to win the duel
- All your performance data will be saved to `game_data.csv`

## Controls

| Action        | Input               |
|---------------|---------------------|
| Shoot         | Left Mouse Button   |
| Reload        | Automatic           |
| Quit Game     | ESC key or UI button|

## Folder Structure

```
Eagle-Eyes/
├── assets/
│   ├── bg/
│   │   ├── desert.png
│   │   └── cloud.png
│   └── sfx/
│       ├── gunshot.wav
│       └── reload.wav
├── main.py
├── requirements.txt
├── game_data.csv
```

## Notes

- Works on Windows, macOS, and Linux
- Developed with Pygame 2.6.1 and Python 3.11.9
- All required assets must be present in the correct directories for the game to run properly
