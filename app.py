from flask import Flask, render_template, Response, jsonify, request
import cv2
import threading
import time
from hand_detector import HandDetector
from gesture_classifier import GestureClassifier

app = Flask(__name__)

# Global variables for sharing data between threads
current_letter = None
letter_confidence = 0.0
notepad_text = ""
last_letter_time = 0
letter_cooldown = 1.0  # Seconds before same letter can be added again
letter_hold_time = 0.5  # Seconds to hold gesture before adding letter
letter_start_time = None
pending_letter = None

# Thread lock for thread-safe operations
lock = threading.Lock()

# Initialize hand detector and classifier (supports 2 hands)
detector = HandDetector(max_hands=2, detection_confidence=0.7, tracking_confidence=0.7)
classifier = GestureClassifier()

# Camera capture
camera = None


def get_camera():
    """Get or initialize camera."""
    global camera
    if camera is None:
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    return camera


def generate_frames():
    """Generate video frames with hand detection overlay."""
    global current_letter, letter_confidence, notepad_text
    global last_letter_time, letter_start_time, pending_letter
    
    cam = get_camera()
    
    while True:
        success, frame = cam.read()
        if not success:
            break
        
        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Detect hands and draw landmarks
        frame, results = detector.find_hands(frame, draw=True)
        
        # Get landmarks for all detected hands
        all_landmarks = detector.get_all_hands_landmarks(results, frame.shape)
        hand_count = len(all_landmarks)
        
        # Show hand count on screen
        cv2.putText(frame, f"Hands: {hand_count}", (frame.shape[1] - 120, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        if all_landmarks:
            # Use two-hand classification if available
            letter, confidence = classifier.classify_two_hands(all_landmarks)
            
            with lock:
                current_letter = letter
                letter_confidence = confidence
                
                current_time = time.time()
                
                # Letter stabilization logic
                if letter is not None:
                    if pending_letter == letter:
                        # Same letter being held
                        if letter_start_time and (current_time - letter_start_time) >= letter_hold_time:
                            # Letter held long enough, add to notepad
                            if (current_time - last_letter_time) >= letter_cooldown:
                                notepad_text += letter
                                last_letter_time = current_time
                                letter_start_time = None  # Reset for next letter
                    else:
                        # New letter detected
                        pending_letter = letter
                        letter_start_time = current_time
            
            # Draw current letter on frame
            if letter:
                cv2.putText(frame, f"Letter: {letter}", (10, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
                cv2.putText(frame, f"Confidence: {confidence:.0%}", (10, 90), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                
                # Draw hold progress bar
                if letter_start_time:
                    hold_progress = min(1.0, (time.time() - letter_start_time) / letter_hold_time)
                    bar_width = int(200 * hold_progress)
                    cv2.rectangle(frame, (10, 110), (210, 130), (100, 100, 100), -1)
                    cv2.rectangle(frame, (10, 110), (10 + bar_width, 130), (0, 255, 0), -1)
                    cv2.putText(frame, "Hold to type", (10, 155), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        else:
            with lock:
                current_letter = None
                letter_confidence = 0.0
                pending_letter = None
                letter_start_time = None
        
        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


@app.route('/')
def index():
    """Serve main page."""
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    """Video streaming route."""
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/get_letter')
def get_letter():
    """Get current detected letter."""
    with lock:
        return jsonify({
            'letter': current_letter,
            'confidence': letter_confidence
        })


@app.route('/get_notepad')
def get_notepad():
    """Get current notepad text."""
    with lock:
        return jsonify({'text': notepad_text})


@app.route('/clear_notepad', methods=['POST'])
def clear_notepad():
    """Clear notepad text."""
    global notepad_text
    with lock:
        notepad_text = ""
    return jsonify({'success': True})


@app.route('/backspace', methods=['POST'])
def backspace():
    """Remove last character from notepad."""
    global notepad_text
    with lock:
        notepad_text = notepad_text[:-1]
    return jsonify({'success': True, 'text': notepad_text})


@app.route('/add_space', methods=['POST'])
def add_space():
    """Add space to notepad."""
    global notepad_text
    with lock:
        notepad_text += " "
    return jsonify({'success': True, 'text': notepad_text})


@app.route('/add_newline', methods=['POST'])
def add_newline():
    """Add newline to notepad."""
    global notepad_text
    with lock:
        notepad_text += "\n"
    return jsonify({'success': True, 'text': notepad_text})


if __name__ == '__main__':
    print("Starting Hand Sign Recognition App (supports 2 hands)...")
    print("Open http://localhost:5000 in your browser")
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
