# 🤟 Hand Sign Recognition App

A real-time hand gesture recognition web application that converts hand signs into text. Make letter shapes with your fingers and watch them appear on screen!

## ✨ Features

- **Real-time Recognition** - Instant detection of hand gestures via webcam
- **Two-Hand Support** - Use one or both hands for gestures
- **Common-Sense Recognition** - Recognizes finger shapes that look like letters
- **Built-in Notepad** - Type messages using hand gestures
- **Hold-to-Type** - Hold a gesture for 0.5 seconds to add the letter

## 🎯 Supported Gestures

| Gesture | Letter | Description |
|---------|--------|-------------|
| ✊ Fist | A | All fingers curled |
| 🖐️ Open Hand | B | All fingers extended, thumb tucked |
| ☝️ One Finger | D | Only index finger pointing up |
| ✌️ V-Shape | V | Index and middle fingers spread apart |
| 🤟 3 Fingers | W | Index, middle, and ring fingers up |
| 👍+☝️ L-Shape | L | Thumb and index extended at right angle |
| 🤙 Thumb+Pinky | Y | Thumb and pinky extended |
| ☝️+✌️ Two Together | U | Index and middle fingers together |
| 👌 Circle | O | Thumb and index forming a circle |
| 🤏 Pinch | F | Thumb and index touching, others extended |

## 🚀 Installation

### Prerequisites
- **Python 3.11 or 3.12** (Required - Python 3.13 is NOT supported due to MediaPipe compatibility)
- Webcam

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Sourabh-beast/hand-sign-app.git
   cd hand-sign-app
   ```

2. **Create virtual environment with Python 3.12**:
   ```bash
   # Windows
   py -3.12 -m venv venv
   
   # Mac/Linux
   python3.12 -m venv venv
   ```

3. **Activate virtual environment**:
   ```bash
   # Windows
   .\venv\Scripts\activate
   
   # Mac/Linux
   source venv/bin/activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🎮 Usage

1. **Start the app**:
   ```bash
   python app.py
   ```

2. **Open browser** at: http://localhost:5000

3. **Allow camera access** when prompted

4. **Make hand gestures** in front of the camera:
   - The detected letter appears on screen
   - Hold a gesture for 0.5 seconds to type it
   - Use the buttons for Space, Enter, Backspace, and Clear

## 🖥️ Interface

- **Camera Feed** - Shows your hand with detected landmarks
- **Detected Letter** - Current recognized letter with confidence %
- **Hold Progress Bar** - Shows how long to hold for typing
- **Hands Counter** - Shows how many hands are detected (1 or 2)
- **Notepad** - Where typed letters appear

## 📁 Project Structure

```
hand-sign-app/
├── app.py               # Main Flask application
├── hand_detector.py     # Hand detection using MediaPipe
├── gesture_classifier.py # Gesture recognition logic
├── requirements.txt     # Python dependencies
├── README.md            # This file
├── .gitignore           # Git ignore rules
├── templates/
│   └── index.html       # Web interface
└── static/
    ├── css/
    │   └── style.css    # Styling
    └── js/
        └── main.js      # Frontend JavaScript
```

## 🔧 Configuration

In `app.py`, you can adjust:
- `letter_cooldown` - Time between same letters (default: 1.0s)
- `letter_hold_time` - How long to hold gesture (default: 0.5s)
- `detection_confidence` - Hand detection threshold (default: 0.7)

## 🛠️ Technologies Used

- **Flask** - Python web framework
- **MediaPipe** - Hand detection and landmark tracking
- **OpenCV** - Camera capture and image processing
- **NumPy** - Numerical computations
- **JavaScript** - Frontend interactivity

## 💡 Tips for Better Recognition

1. **Good lighting** - Ensure your hand is well-lit
2. **Plain background** - Simple backgrounds work better
3. **Clear gestures** - Make distinct finger positions
4. **Steady hand** - Hold gestures still for recognition
5. **Full hand visible** - Keep your entire hand in frame

## ❓ Troubleshooting

| Issue | Solution |
|-------|----------|
| `No module named 'mediapipe'` | Use Python 3.11 or 3.12 (not 3.13) |
| Camera not working | Check browser permissions |
| No hand detected | Improve lighting, move closer |
| Wrong letters | Make gestures more distinct |
| App won't start | Check if port 5000 is free |

## 📋 Requirements

```
flask
opencv-python
mediapipe
numpy
```

## 📝 License

This project is open source and available for personal and educational use.

---

Made with ❤️ using Python, Flask, and MediaPipe
