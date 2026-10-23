# dinosaur_battle

🦖 Hand Tracking Dinosaur Battle

A fun, two-player dinosaur shooting game built with Python, OpenCV, and MediaPipe!

Control your rockets using your hands, shoot lasers by pinching your fingers, and compete to get the highest score before time runs out.

No game controller needed — just your webcam and your hands! 🚀

## 🎮 How to Play

🔵 Left hand: Controls the blue rocket

🟠 Right hand: Controls the orange rocket

☝️ Move your index finger: Move your rocket freely in any direction (up, down, left, or right)

🤏 Pinch your thumb and index finger: Shoot a laser upward

🦖 Shoot dinosaurs matching your rocket's color: +1 point

❌ Shoot dinosaurs of the wrong color: −1 point

⏱️ 60-second game: The player with the highest score wins!

Dinosaurs fall from the top of the screen in two colors: blue and orange.

## ✨ Features

Real-time hand tracking using MediaPipe

Two-player gameplay using a single webcam

Free 2D rocket movement controlled by index fingertips

Pinch gesture detection for shooting

Index fingertip and thumb tracking visualization

Color-matching shooting mechanics

Falling dinosaurs in blue and orange

Live score tracking and countdown timer

Winner announcement at the end of each game

## 🛠️ Technologies Used

Python — Game logic

OpenCV — Webcam capture and game rendering

MediaPipe — Hand landmark detection

NumPy — Image processing

## 🚀 Getting Started

### 1. Clone the repository
```
git clone https://github.com/peraverse/dinosaur_battle.git

cd dinosaur_battle
```
### 2. Create a virtual environment
```
python3 -m venv .venv
```
Activate it on macOS/Linux:
```
source .venv/bin/activate
```
On Windows:
```
.venv\Scripts\Activate.ps1
```
### 3. Install dependencies
```
python -m pip install opencv-python mediapipe numpy
```
### 4. Download the hand-tracking model
Download the [MediaPipe Hand Landmarker model](https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task).

Save it in your project folder as hand_landmarker.task.
### 5. Run the game
python main.py

### Note
Allow camera access when prompted.

## 📁 Project Structure
```
dinosaur-battle/
├── main.py
├── hand_landmarker.task
└── README.md
```

## 💡 What You Can Learn

This project is a practical introduction to:

Computer vision and real-time webcam processing

Hand landmark detection using MediaPipe

Gesture recognition through landmark distances

Mapping hand coordinates to game controls

Game loops, object movement, and collision detection

Two-player interactive game development with Python

## 📝 Notes

This game runs locally using Python, not directly in a web browser.

A webcam is required.

Good lighting helps improve hand-tracking accuracy.

Both hands should remain visible to the camera for reliable gameplay.

## 🤖 About RoboSpace

RoboSpace is a space for curious minds to explore robotics, programming, AI, engineering, and technology through fun projects, tutorials, and easy-to-understand explanations.

🌐 Follow RoboSpace

🎬 YouTube: [RoboSpace - จุดนัดบอท](https://www.youtube.com/@RoboSpaceTH)

📸 Instagram: [robospace.th](https://www.instagram.com/robospace.th?igsi=MTFzaHI0ZHZ5ZGpxdw%3D%3D&utm_source=qr)


