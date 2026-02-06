# 🏓 Hand Pong: AI-Powered Gesture Control

[![Poster](https://img.shields.io/badge/View-Project_Poster-8b0000)](./Poster.pdf)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![MediaPipe](https://img.shields.io/badge/Computer_Vision-MediaPipe-orange)
![Status](https://img.shields.io/badge/Status-Finished-green)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

> **A contactless, gesture-controlled Pong game demonstrating advanced Human-Computer Interaction (HCI) and Signal Processing.**

**Hand Pong** reinvents the classic arcade game using modern **AI and Computer Vision**. Instead of a physical controller, the player controls the paddle using the **angle of their thumb**. The project features a robust **Adaptive Smoothing Algorithm** to filter hand jitter, ensuring precision gameplay comparable to hardware mice.

<img width="900" height="951" alt="HandPong" src="https://github.com/user-attachments/assets/3778fb9d-6977-44ad-a05b-3fa7d7c99098" />

*Figure 1: Main gameplay interface.*

---

## 🚀 Key Features

* **🖐 Contactless Control:** Play using only a standard webcam. No mouse, keyboard, or sensors required.
* **📐 Angle-Based Input:** Unique control scheme based on the thumb-to-hand angle (100°–250°) rather than simple x/y coordinates.
* **🧠 Smart Signal Processing:** Implements an **Adaptive Exponential Moving Average (EMA)** filter to reduce sensor noise and jitter.
* **🎓 Dual-Task Mode:** Players could solve math equations using finger gestures (showing 0-5 fingers) while playing, testing cognitive load.
* **📊 Built-in Analytics:** Includes a `DataRecorder` module to capture raw sensor data and validate filter performance.

---

## 🎮 How it Works

### 1. The Control Mechanism
Unlike traditional gesture games that track hand position, Hand Pong tracks **hand posture**.
The system calculates the vector angle between the **Thumb Tip** and the **Hand Anchor Point**.

<img width="300" height="539" alt="grafik" src="https://github.com/user-attachments/assets/ada8813b-419e-44f5-9b35-65c8e21b51b7" />

*Figure 2: Visualizing the thumb angle calculation using MediaPipe landmarks.*

### 2. Gesture Commands
The system recognizes semantic gestures for game flow:
* **Navigation:** Show **1, 2, or 3 fingers** to select menu options.
* **Pause:** Cross index fingers in an **"X" shape**.
* **Math Answers:** Show **0-5 fingers** to answer in-game questions and unlock Power-Ups.

---

## ⚙️ Configuration & Customization

The game is designed to be flexible. You can adjust physics, rules, and input sensitivity in `src/config.py` without changing the core code.

**Key Settings:**
* **Accessibility:** Switch between **Left or Right** hand dominance.
* **Gameplay:** Adjust `WIN_SCORE`, `BALL_SPEED`, or `TIME_LIMIT`.
* **Power-Ups:** Configure duration for effects like *Tiny Ball* or *Paddle Shrink*.

```python
# src/config.py

DOMINANT_HAND = "Right"       # Options: "Left", "Right"
WIN_SCORE = 5                 # Goals required to win
SUDDEN_DEATH = True           # Enable sudden death mode
PADDLE_ANGLE_UP = 100.0       # Angle for top position
PADDLE_ANGLE_DOWN = 250.0     # Angle for bottom position
...
```
## 🛠️ Installation

### Prerequisites
* **Python 3.8** or higher
* A standard **Webcam**

### Setup Guide
1. **Clone the repository:**
   ```bash
   git clone https://github.com/AlhaririAnas/HandPong.git
   cd HandPong
    ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
     ```
3. **Run the game:**
    ```bash
   python main.py --play
   ```

---

## 📊 Technical Analysis & Methodology

To ensure professional-grade control, I conducted a quantitative performance study to evaluate the reliability of **MediaPipe** landmarks and the effectiveness of my signal processing logic.

### 1. Methodology
My approach followed a three-step data-driven pipeline:
* **Recording:** Using the custom `DataRecorder.py`, I captured raw thumb-angle data across 10 different target angles.
* **Dynamic Smoothing:** To bridge the gap between stability and speed, the system utilizes an **Adaptive EMA filter**. By adjusting the smoothing weight ($\alpha$) in real-time based on the rate of change in hand movement, it eliminates micro-jitters during steady poses while maintaining zero-lag performance during rapid paddle movements.
* **Validation:** I used `performance_analysis.ipynb` to compare the raw AI signal against the filtered output to calculate precise error reduction.

### 2. Signal Stability Analysis
The first plot illustrates the real-time performance of the adaptive filter. While the raw MediaPipe signal (Salmon) exhibits optical noise, the filtered signal (Blue) remains stable within the target corridor.

<img width="769" height="382" alt="grafik" src="https://github.com/user-attachments/assets/8e0a056f-c04e-4ae2-b961-8316ae3cdb5c" />

*Figure 3: Real-time signal stabilization showing jitter reduction.*

### 3. Quantitative Results & Reliability
The second plot shows the accuracy across the entire operational range. By applying the adaptive filter, I achieved a **15.9% reduction in Mean Absolute Error (MAE)**.

* **Raw MediaPipe MAE:** ~1.13°
* **Filtered MAE:** ~0.95°

<img width="1377" height="820" alt="grafik" src="https://github.com/user-attachments/assets/06f425d1-fc0e-4cd7-974b-eceea6773c6e" />

*Figure 4: Accuracy comparison (% of frames within ±1.0° tolerance).*

This methodology proves that while MediaPipe provides a robust foundation, custom signal processing is essential for high-precision, AI-based gaming interfaces.


> 💡 **Deep Dive:** For a high-level visual summary of my methodology and the full experimental results, check out the [**Project Poster (PDF)**](./Poster.pdf).
---

## 🤝 Support & Contribution

If you have any questions, encounter issues, or want to suggest new features (like new power-ups or gestures), feel free to open an **Issue**. 

I appreciate your interest in the **Hand Pong** project! Whether it's bug fixes or performance improvements in signal processing, your feedback is welcome.

## 📜 License

This project is licensed under the **MIT License** - see the `LICENSE` file for details.

## ✍️ Author

* **Anas Alhariri** - [GitHub Profile](https://github.com/AlhaririAnas)
* *Developed for the module "Advances in Intelligent Systems"*
