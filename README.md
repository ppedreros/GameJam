<div align="center">
  <img width="769" height="150" alt="image" src="https://github.com/user-attachments/assets/366e6681-ea70-4340-91b8-68985275f282" />
</div>
<div align="center">

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Raylib](https://img.shields.io/badge/raylib-5.5-lightgrey.svg)](https://www.raylib.com/)

</div>


**Combo Crush** is a fast-paced, 3D competitive rhythm/reaction jumping game built with Python and Raylib (`pyray`).

Jump rapidly along an infinite neon highway by matching your keyboard inputs to the arrows on incoming platforms. Survive as long as you can in Solo Mode, or face off against a friend in a chaotic Local Split-Screen Multiplayer match to see who has the fastest reflexes!

## 🌟 Features

* **⚡ High-Speed Reflex Gameplay:** Read the upcoming platform arrows and press the corresponding directions to jump seamlessly without breaking a sweat.
* **🔥 INSANE Combo System:** Chain jumps without mistakes to build up your combo! Triggers dynamic neon visuals, screen shakes, and custom voice/sound effects at major milestones (x5, x10, x15, x20, x30).
* **👥 Local Multiplayer (Split-Screen):** Race against a friend. The longer you survive, the harder it gets. Sabotage each other by triggering traps!
* **☠️ Dynamic Traps & Modifiers:**
  * **Inverted Controls:** Purple platforms reverse your input required.
  * **Darkness:** Plunges the screen into a small spotlight mode.
  * **Screen Swap (2P):** Suddenly swaps your screen, identity, and controls with your opponent mid-game!
  * **Forks & Active Traps:** Choose alternate paths. Touching a trap triggers a "DODGE!" quick-time event for your opponent—fail it, and suffer Time Drain, Freeze (Stun), or Darkness.
* **🎯 Minigames & Battles:** Break up the jumping action with sudden minigames!
  * **Mashing Minigame:** Mash the button as fast as you can to fill your neon glass with liquid (features spring-physics sloshing!).
  * **Arrow Battles:** A quick reaction duel. First to press the correct sequence of arrows wins!
* **👑 Global Scoring (Crown System):** It's not just about distance. Winning minigames or battles earns you **Bonus Points** and **Crowns**. The final "Game Over" screen calculates the absolute winner weighing all factors.

## 🕹️ Controls

| Action | Player 1 (Left Screen) | Player 2 (Right Screen) |
| :--- | :--- | :--- |
| **Jump Forward** | `W` | `Up Arrow` |
| **Jump Left** | `A` | `Left Arrow` |
| **Jump Right** | `D` | `Right Arrow` |
| **Jump Back** | `S` | `Down Arrow` |
| **Minigame Mash** | `W` (or `Space` in Solo) | `Up Arrow` |

## 🚀 How to Play (No Installation Required!)

Want to play immediately? You don't need Python or any special software.

1. **Download the Game**: Download the [`ComboCrush.zip`](https://github.com/ppedreros/GameJam/blob/main/ComboCrush.zip) file from the latest Release.
2. **Extract**: Right-click the `.zip` and select **"Extract All..."**.
3. **Play**: Open the folder and double-click **`ComboCrush.exe`** (the blue icon) to launch the game!

*(Note: Windows might show a "Windows protected your PC" popup because this is an Indie game. Just click "More info" and then "Run anyway").*

---

## 🛠️ Developer Setup (Running from source)

If you're a developer and want to run the raw Python code or build it yourself:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/ComboCrush.git
   cd ComboCrush
   ```

2. **Install dependencies:**

   The project uses `raylib-python-cffi`. It's highly recommended to use `uv` or a virtual environment:

   ```bash
   pip install raylib
   ```

3. **Run the game:**

   ```bash
   python main.py
   ```

### 📦 Building the Executable

To generate your own `.exe` using PyInstaller:

```bash
pip install pyinstaller
pyinstaller --noconfirm --onedir --windowed --add-data "assets;assets" --name "ComboCrush" main.py
```
You will find the executable inside the `dist/ComboCrush/` directory.

## 👨‍💻 Team

* **Juan David Cepeda** - [GitHub](https://github.com/DavidCepeda13)
* **Pablo Pedreros** - [GitHub](https://github.com/ppedreros)
* **Jorge** - [GitHub](https://github.com/Pekkads)
* **Juan Felipe Hernández** - [GitHub](https://github.com/jfh000)

## 🎵 Assets & Credits

* **Engine:** Powered by [Raylib](https://www.raylib.com/) via `pyray`.
* **Graphics:** Procedural 3D primitive rendering with neon/bloom-like composite shaders and particle systems.
* **Audio:** SFX and music are loaded dynamically from the `assets/sounds` directory (ensure all `.mp3` and `.wav` files are present).

## 📄 License

This project was built during a Game Jam. Feel free to fork, modify, and learn from the codebase!

---
*Happy Jumping!*
