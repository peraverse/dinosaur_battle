
import cv2
import mediapipe as mp
import numpy as np
import math
import time
import random
from pathlib import Path

# =====================================
# 1. GAME SETTINGS
# =====================================

WIDTH = 960
HEIGHT = 600

GAME_DURATION = 60
DINOSAUR_SPAWN_INTERVAL = 0.25
DINOSAUR_SPEED_MIN = 70
DINOSAUR_SPEED_MAX = 150

LASER_SPEED = 850

PINCH_THRESHOLD = 0.8
RELEASE_THRESHOLD = 0.82

BLUE = (255, 150, 50)
ORANGE = (0, 150, 255)
YELLOW = (0, 255, 255)
WHITE = (255, 255, 255)
RED = (0, 0, 255)

# =====================================
# 2. MEDIAPIPE SETUP
# =====================================

model_path = (
    Path(__file__).resolve().parent
    / "hand_landmarker.task"
)

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
Options = mp.tasks.vision.HandLandmarkerOptions
RunningMode = mp.tasks.vision.RunningMode

options = Options(
    base_options=BaseOptions(
        model_asset_path=str(model_path)
    ),
    running_mode=RunningMode.VIDEO,
    num_hands=2
)

# =====================================
# 3. GAME DATA
# =====================================

players = {
    "Left": {
        "x": WIDTH // 4,
        "y": HEIGHT // 2,
        "color": BLUE,
        "score": 0,
        "pinching": False,
        "visible": False
    },
    "Right": {
        "x": WIDTH * 3 // 4,
        "y": HEIGHT // 2,
        "color": ORANGE,
        "score": 0,
        "pinching": False,
        "visible": False
    }
}

lasers = []
dinosaurs = []

game_started = False
game_over = False

game_start_time = 0
last_spawn_time = 0

def distance(a, b):
    return math.hypot(
        a.x - b.x,
        a.y - b.y
    )

# =====================================
# 4. DRAW DINOSAUR
# =====================================

def draw_dinosaur(screen, dino):

    x = int(dino["x"])
    y = int(dino["y"])
    color = dino["color"]

    # Body
    cv2.ellipse(
        screen, (x, y),
        (20, 15), 0, 0, 360,
        color, -1
    )

    # Tail
    tail = np.array([
        [x - 15, y],
        [x - 38, y - 12],
        [x - 27, y + 12]
    ], dtype=np.int32)

    cv2.fillPoly(screen, [tail], color)

    # Neck
    cv2.rectangle(
        screen,
        (x + 10, y - 25),
        (x + 22, y),
        color, -1
    )

    # Head
    cv2.circle(
        screen,
        (x + 20, y - 23),
        13, color, -1
    )

    # Eye
    cv2.circle(
        screen,
        (x + 24, y - 27),
        4, WHITE, -1
    )

    cv2.circle(
        screen,
        (x + 25, y - 27),
        2, (0, 0, 0), -1
    )

    # Legs
    cv2.line(
        screen,
        (x - 8, y + 10),
        (x - 8, y + 24),
        color, 6
    )

    cv2.line(
        screen,
        (x + 8, y + 10),
        (x + 8, y + 24),
        color, 6
    )

# =====================================
# 5. START / RESET GAME
# =====================================

def start_game():

    global game_started
    global game_over
    global game_start_time
    global last_spawn_time

    game_started = True
    game_over = False

    game_start_time = time.monotonic()
    last_spawn_time = game_start_time

    lasers.clear()
    dinosaurs.clear()

    for player in players.values():
        player["score"] = 0
        player["pinching"] = False

# =====================================
# 6. OPEN CAMERA
# =====================================

cap = cv2.VideoCapture(
    0,
    cv2.CAP_AVFOUNDATION
)

if not cap.isOpened():
    raise RuntimeError("Cannot open camera")

previous_time = time.monotonic()
timestamp_ms = 0

# =====================================
# 7. MAIN GAME LOOP
# =====================================

with HandLandmarker.create_from_options(options) as detector:

    while True:

        now = time.monotonic()
        dt = min(now - previous_time, 0.05)
        previous_time = now

        ret, frame = cap.read()

        if not ret:
            break

        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (WIDTH, HEIGHT))

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )

        timestamp_ms += max(1, int(dt * 1000))

        result = detector.detect_for_video(
            mp_image,
            timestamp_ms
        )

        screen = cv2.addWeighted(
            frame,
            0.25,
            np.zeros_like(frame),
            0.75,
            0
        )

        # ---------------------------------
        # 8. TRACK HANDS
        # ---------------------------------

        for player in players.values():
            player["visible"] = False

        for i, landmarks in enumerate(result.hand_landmarks):

            detected_label = (
                result.handedness[i][0].category_name
            )

            # Keep your corrected hand mapping
            label = (
                "Right"
                if detected_label == "Left"
                else "Left"
            )

            player = players[label]
            player["visible"] = True

            thumb = landmarks[4]
            index = landmarks[8]

            player["x"] = int(index.x * WIDTH)
            player["y"] = int(index.y * HEIGHT)

            thumb_x = int(thumb.x * WIDTH)
            thumb_y = int(thumb.y * HEIGHT)

            hand_width = max(
                distance(landmarks[5], landmarks[17]),
                0.001
            )

            pinch_ratio = (
                distance(thumb, index) / hand_width
            )

            if (
                game_started
                and not game_over
                and pinch_ratio < PINCH_THRESHOLD
                and not player["pinching"]
            ):
                lasers.append({
                    "x": player["x"],
                    "y": player["y"] - 25,
                    "color": player["color"],
                    "owner": label
                })

                player["pinching"] = True

            elif pinch_ratio > RELEASE_THRESHOLD:
                player["pinching"] = False

            # Thumb marker
            cv2.circle(
                screen,
                (thumb_x, thumb_y),
                10, YELLOW, -1
            )

            cv2.putText(
                screen, "Thumb",
                (thumb_x + 12, thumb_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5, YELLOW, 1
            )

        # ---------------------------------
        # 9. UPDATE GAME
        # ---------------------------------

        if game_started and not game_over:

            remaining = max(
                0,
                GAME_DURATION - (now - game_start_time)
            )

            if remaining <= 0:
                game_over = True

            else:

                # Spawn dinosaurs
                if (
                    now - last_spawn_time
                    >= DINOSAUR_SPAWN_INTERVAL
                ):
                    dinosaurs.append({
                        "x": random.randint(40, WIDTH - 40),
                        "y": -40,
                        "color": random.choice(
                            [BLUE, ORANGE]
                        ),
                        "speed": random.uniform(
                            DINOSAUR_SPEED_MIN,
                            DINOSAUR_SPEED_MAX
                        )
                    })

                    last_spawn_time = now

                # Move dinosaurs
                for dino in dinosaurs:
                    dino["y"] += dino["speed"] * dt

                # Move lasers
                for laser in lasers:
                    laser["y"] -= LASER_SPEED * dt

                # Detect collisions
                hit_lasers = set()
                hit_dinosaurs = set()

                for li, laser in enumerate(lasers):

                    for di, dino in enumerate(dinosaurs):

                        if di in hit_dinosaurs:
                            continue

                        dx = laser["x"] - dino["x"]
                        dy = laser["y"] - dino["y"]

                        if math.hypot(dx, dy) < 30:

                            owner = laser["owner"]
                            player = players[owner]

                            if (
                                player["color"]
                                == dino["color"]
                            ):
                                player["score"] += 1
                            else:
                                player["score"] -= 1

                            hit_lasers.add(li)
                            hit_dinosaurs.add(di)
                            break

                lasers = [
                    laser
                    for i, laser in enumerate(lasers)
                    if i not in hit_lasers
                    and laser["y"] > -30
                ]

                dinosaurs = [
                    dino
                    for i, dino in enumerate(dinosaurs)
                    if i not in hit_dinosaurs
                    and dino["y"] < HEIGHT + 40
                ]

        # ---------------------------------
        # 10. DRAW DINOSAURS
        # ---------------------------------

        for dino in dinosaurs:
            draw_dinosaur(screen, dino)

        # ---------------------------------
        # 11. DRAW LASERS
        # ---------------------------------

        for laser in lasers:

            x = int(laser["x"])
            y = int(laser["y"])

            cv2.line(
                screen,
                (x, y),
                (x, y - 25),
                laser["color"],
                4
            )

        # ---------------------------------
        # 12. DRAW ROCKETS
        # ---------------------------------

        for label, player in players.items():

            if not player["visible"]:
                continue

            x = player["x"]
            y = player["y"]

            points = np.array([
                [x, y - 25],
                [x - 18, y + 20],
                [x + 18, y + 20]
            ], dtype=np.int32)

            cv2.fillPoly(
                screen,
                [points],
                player["color"]
            )

            cv2.circle(
                screen,
                (x, y),
                5, WHITE, -1
            )

        # ---------------------------------
        # 13. DRAW SCORES AND TIMER
        # ---------------------------------

        cv2.putText(
            screen,
            f"LEFT: {players['Left']['score']}",
            (20, 45),
            cv2.FONT_HERSHEY_SIMPLEX,
            1, BLUE, 2
        )

        cv2.putText(
            screen,
            f"RIGHT: {players['Right']['score']}",
            (WIDTH - 230, 45),
            cv2.FONT_HERSHEY_SIMPLEX,
            1, ORANGE, 2
        )

        if not game_started:
            message = "Press S to Start"

        elif game_over:

            left_score = players["Left"]["score"]
            right_score = players["Right"]["score"]

            if left_score > right_score:
                message = "LEFT WINS!"
            elif right_score > left_score:
                message = "RIGHT WINS!"
            else:
                message = "DRAW!"

        else:
            remaining = max(
                0,
                GAME_DURATION - (now - game_start_time)
            )
            message = f"TIME: {int(math.ceil(remaining))}"

        cv2.putText(
            screen,
            message,
            (WIDTH // 2 - 145, 45),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9, WHITE, 2
        )

        cv2.putText(
            screen,
            "Pinch = Shoot | S = Start/Restart | Q = Quit",
            (170, HEIGHT - 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65, WHITE, 2
        )

        cv2.imshow(
            "Dinosaur Battle",
            screen
        )

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

        elif key == ord("s"):
            start_game()

cap.release()
cv2.destroyAllWindows()
