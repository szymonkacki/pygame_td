# 🏰 Pygame Tower Defense Game

*[Przeczytaj po polsku](README.md)*

A fully functional Tower Defense game created in Python using the Pygame library. The goal of the game is to defend against incoming waves of enemies by strategically placing and upgrading defensive towers.

## Main features

* **Tower and evolution system:**
  * Building basic archer towers.
  * Upgrading towers (levels 1-3) to increase damage and range.
  * **Evolution** at the maximum 4th level. Choose between:
    * 🔥 **FireTower** – Area of Effect (AoE) damage.
    * ❄️ **IceTower** – Slows down hit targets.
    * ⚡ **SpeedyTower** – Drastically increased fire rate.
* **Diverse enemies:** Three enemy classes requiring different strategies (Normal, Fast, Durable Tanks).
* **Economy management:** Earn gold by defeating enemies. Invest money in new buildings, upgrades, or recover part of the costs by selling existing towers.
* **Increasing difficulty waves:** With each wave, the number of enemies and the chance of stronger units appearing increases.
* **Full UI:** Main menu, difficulty selection (Normal/Hard), interactive evolution menu, volume slider, and game over screen.

## 🛠️ Requirements

The project uses the `pygame` package.

* Python 3.x
* pygame >= 2.0.0

## 📥 Installation and running

1. Clone the repository to your local machine:
   ```bash
   git clone https://github.com/szymonkacki/pygame_td.git
   ```
2. Navigate to the project folder:
   ```bash
   cd pygame_td
   ```
3. Install the required libraries:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the game:
   ```bash
   python main.py
   ```
## 🎮 In-game controls
* LMB (Left Mouse Button): Build a tower in an empty slot and interact with menu buttons.
* RMB (Right Mouse Button): Click on a tower to upgrade it. If the tower has reached level 3, RMB opens the evolution menu.
* MMB (Middle Mouse Button / Scroll): Click on a tower to sell it and get a partial refund.
* ESC: Open the pause menu during gameplay.

## 💡 Technical information
The code is organized according to the Object-Oriented Programming (OOP) paradigm and divided into structural modules (e.g., game_manager.py, tower.py, enemy.py, bullet.py), ensuring readability and making it easier to introduce new features.
