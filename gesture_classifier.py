import numpy as np

class GestureClassifier:
    """
    Common-sense alphabet gesture classifier.
    Recognizes letters based on how finger shapes visually resemble alphabet letters.
    Supports both single-hand and two-hand gestures.
    """
    
    def __init__(self):
        """Initialize the gesture classifier."""
        self.letters = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        self.current_letter = None
        self.confidence = 0.0
        
        # Finger tip indices
        self.finger_tips = {
            'thumb': 4,
            'index': 8,
            'middle': 12,
            'ring': 16,
            'pinky': 20
        }
        
        # Finger base (MCP) indices
        self.finger_bases = {
            'thumb': 2,
            'index': 5,
            'middle': 9,
            'ring': 13,
            'pinky': 17
        }
        
    def _get_finger_state(self, landmarks):
        """
        Determine if each finger is extended or curled.
        
        Returns:
            dict: State of each finger (True=extended, False=curled)
        """
        if landmarks is None or len(landmarks) != 21:
            return None
            
        finger_states = {}
        
        # Thumb: Check x-distance
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        thumb_mcp = landmarks[2]
        finger_states['thumb'] = abs(thumb_tip[0] - thumb_mcp[0]) > abs(thumb_ip[0] - thumb_mcp[0]) * 0.8
        
        # Other fingers: tip above PIP joint = extended
        for finger, tip_idx in self.finger_tips.items():
            if finger == 'thumb':
                continue
            tip = landmarks[tip_idx]
            pip = landmarks[tip_idx - 2]  # PIP is 2 indices before tip
            finger_states[finger] = tip[1] < pip[1]
        
        return finger_states
    
    def _count_extended(self, finger_states):
        """Count extended fingers (excluding thumb)."""
        if not finger_states:
            return 0
        count = 0
        for finger in ['index', 'middle', 'ring', 'pinky']:
            if finger_states.get(finger, False):
                count += 1
        return count
    
    def _get_distances(self, landmarks):
        """Calculate key distances between landmarks."""
        if landmarks is None:
            return None
            
        def dist(p1, p2):
            return np.sqrt((landmarks[p1][0] - landmarks[p2][0])**2 + 
                          (landmarks[p1][1] - landmarks[p2][1])**2)
        
        palm_size = dist(0, 9)
        if palm_size == 0:
            palm_size = 1
            
        return {
            'thumb_index': dist(4, 8) / palm_size,
            'thumb_middle': dist(4, 12) / palm_size,
            'thumb_ring': dist(4, 16) / palm_size,
            'thumb_pinky': dist(4, 20) / palm_size,
            'index_middle': dist(8, 12) / palm_size,
            'middle_ring': dist(12, 16) / palm_size,
            'ring_pinky': dist(16, 20) / palm_size,
            'palm_size': palm_size,
            'index_pinky': dist(8, 20) / palm_size,
        }
    
    def _get_finger_direction(self, landmarks, finger):
        """Get direction of a finger (up, down, left, right)."""
        tip_idx = self.finger_tips[finger]
        base_idx = self.finger_bases[finger]
        
        tip = landmarks[tip_idx]
        base = landmarks[base_idx]
        
        dx = tip[0] - base[0]
        dy = tip[1] - base[1]
        
        if abs(dx) > abs(dy):
            return 'right' if dx > 0 else 'left'
        else:
            return 'down' if dy > 0 else 'up'
    
    def _fingers_touching(self, landmarks, f1_idx, f2_idx, threshold=0.15):
        """Check if two finger tips are close together."""
        d = self._get_distances(landmarks)
        if d is None:
            return False
        dist = np.sqrt((landmarks[f1_idx][0] - landmarks[f2_idx][0])**2 + 
                       (landmarks[f1_idx][1] - landmarks[f2_idx][1])**2)
        return dist / d['palm_size'] < threshold
    
    def classify(self, landmarks):
        """
        Classify hand gesture based on common-sense letter shapes.
        
        The recognition is based on how fingers visually look like letters:
        - One finger up looks like 'I' or '1'
        - Two fingers spread looks like 'V'
        - Thumb and index forming L looks like 'L'
        - Circle with fingers looks like 'O' or 'C'
        etc.
        
        Args:
            landmarks: List of 21 (x, y, z) landmark tuples
            
        Returns:
            tuple: (letter, confidence) or (None, 0) if no detection
        """
        if landmarks is None:
            return None, 0.0
        
        finger_states = self._get_finger_state(landmarks)
        if finger_states is None:
            return None, 0.0
            
        d = self._get_distances(landmarks)
        extended = self._count_extended(finger_states)
        thumb_up = finger_states['thumb']
        
        letter = None
        confidence = 0.75
        
        # ============ COMMON SENSE LETTER RECOGNITION ============
        
        # === FIST SHAPES ===
        # A - Fist (all fingers curled)
        if extended == 0 and not thumb_up:
            letter = 'A'
            confidence = 0.80
        
        # S - Fist with thumb over fingers
        elif extended == 0 and thumb_up:
            letter = 'S'
            confidence = 0.75
        
        # === ONE FINGER ===
        # I - Single pinky extended (looks like lowercase i)
        elif (finger_states['pinky'] and not finger_states['index'] and 
              not finger_states['middle'] and not finger_states['ring']):
            if not thumb_up:
                letter = 'I'
                confidence = 0.85
            else:
                letter = 'Y'  # Pinky + thumb = Y
                confidence = 0.90
        
        # D - Index finger pointing up (like number 1)
        elif (finger_states['index'] and not finger_states['middle'] and 
              not finger_states['ring'] and not finger_states['pinky']):
            index_dir = self._get_finger_direction(landmarks, 'index')
            if not thumb_up:
                if index_dir == 'up':
                    letter = 'D'
                    confidence = 0.80
                else:
                    letter = 'G'  # Pointing sideways
                    confidence = 0.75
            else:
                # L shape - thumb and index extended
                letter = 'L'
                confidence = 0.85
        
        # === TWO FINGERS ===
        # V - Two fingers spread (peace sign looks like V)
        elif (finger_states['index'] and finger_states['middle'] and 
              not finger_states['ring'] and not finger_states['pinky']):
            if d['index_middle'] > 0.5:
                letter = 'V'
                confidence = 0.90
            elif d['index_middle'] < 0.3:
                if thumb_up:
                    letter = 'K'  # Two fingers up with thumb
                    confidence = 0.75
                else:
                    letter = 'U'  # Two fingers together
                    confidence = 0.80
            else:
                letter = 'H'  # Two fingers, medium spread
                confidence = 0.70
        
        # R - Index and middle crossed (looks like R)
        elif (finger_states['index'] and finger_states['middle'] and 
              not finger_states['ring'] and not finger_states['pinky']):
            if d['index_middle'] < 0.25:
                letter = 'R'
                confidence = 0.75
        
        # === THREE FINGERS ===
        # W - Three fingers up (index, middle, ring - looks like W)
        elif (finger_states['index'] and finger_states['middle'] and 
              finger_states['ring'] and not finger_states['pinky']):
            letter = 'W'
            confidence = 0.85
        
        # === FOUR/FIVE FINGERS ===
        # B - All four fingers extended, thumb tucked
        elif (finger_states['index'] and finger_states['middle'] and 
              finger_states['ring'] and finger_states['pinky'] and not thumb_up):
            if d['index_pinky'] < 1.0:
                letter = 'B'
                confidence = 0.85
            else:
                letter = 'B'
                confidence = 0.70
        
        # 5/Open - All fingers including thumb
        elif extended == 4 and thumb_up:
            letter = 'B'  # Open hand = B
            confidence = 0.70
        
        # === CIRCLE/CURVED SHAPES ===
        # O - Fingers form circle (thumb touching index)
        elif d['thumb_index'] < 0.4 and extended <= 1:
            letter = 'O'
            confidence = 0.80
        
        # C - Curved hand like holding something
        elif d['thumb_index'] > 0.4 and d['thumb_index'] < 1.0:
            if extended >= 2 and d['thumb_pinky'] < 1.5:
                letter = 'C'
                confidence = 0.75
        
        # F - Thumb and index touching, other fingers up
        elif (finger_states['middle'] and finger_states['ring'] and 
              finger_states['pinky'] and d['thumb_index'] < 0.35):
            letter = 'F'
            confidence = 0.80
        
        # === SPECIAL SHAPES ===
        # E - All fingers curled toward palm
        elif extended == 0:
            letter = 'E'
            confidence = 0.70
        
        # M - Three fingers down over thumb
        elif not finger_states['index'] and not finger_states['middle'] and not finger_states['ring']:
            if not finger_states['pinky']:
                letter = 'M'
                confidence = 0.65
        
        # N - Two fingers down over thumb
        elif not finger_states['index'] and not finger_states['middle']:
            if finger_states['ring'] or finger_states['pinky']:
                letter = 'N'
                confidence = 0.65
        
        # T - Thumb between index and middle
        elif not finger_states['index'] and not finger_states['middle']:
            if d['thumb_index'] < 0.4 and d['thumb_middle'] < 0.5:
                letter = 'T'
                confidence = 0.65
        
        # X - Index finger bent/hooked
        elif not finger_states['index'] and not finger_states['middle']:
            index_tip = landmarks[8]
            index_pip = landmarks[6]
            if index_tip[1] > index_pip[1]:
                letter = 'X'
                confidence = 0.70
        
        # P - Index pointing down
        elif finger_states['index'] and finger_states['middle']:
            index_dir = self._get_finger_direction(landmarks, 'index')
            if index_dir == 'down':
                letter = 'P'
                confidence = 0.70
        
        # Q - Thumb and index pointing down together
        elif finger_states['index'] and thumb_up:
            index_dir = self._get_finger_direction(landmarks, 'index')
            if index_dir == 'down':
                letter = 'Q'
                confidence = 0.70
        
        # J - Pinky doing hook motion (static: just pinky)
        elif finger_states['pinky'] and not finger_states['index']:
            letter = 'J'
            confidence = 0.65
        
        # Z - Index pointing (static version of Z motion)
        elif (finger_states['index'] and not finger_states['middle'] and 
              not finger_states['ring'] and not finger_states['pinky']):
            letter = 'Z'
            confidence = 0.60
        
        # === FALLBACK ===
        if letter is None:
            if extended == 0:
                letter = 'A'
                confidence = 0.50
            elif extended == 1:
                letter = 'D'
                confidence = 0.50
            elif extended == 2:
                letter = 'V'
                confidence = 0.50
            elif extended == 3:
                letter = 'W'
                confidence = 0.50
            elif extended == 4:
                letter = 'B'
                confidence = 0.50
        
        self.current_letter = letter
        self.confidence = confidence
        
        return letter, confidence
    
    def classify_two_hands(self, landmarks_list):
        """
        Classify gestures using two hands together.
        Some letters can be formed using both hands.
        
        Args:
            landmarks_list: List of landmark lists (one per hand)
            
        Returns:
            tuple: (letter, confidence) or result from single hand
        """
        if not landmarks_list:
            return None, 0.0
        
        if len(landmarks_list) == 1:
            return self.classify(landmarks_list[0])
        
        # Two hands detected - try to recognize two-hand gestures
        hand1 = landmarks_list[0]
        hand2 = landmarks_list[1]
        
        fs1 = self._get_finger_state(hand1)
        fs2 = self._get_finger_state(hand2)
        
        if fs1 is None or fs2 is None:
            return self.classify(hand1)
        
        ext1 = self._count_extended(fs1)
        ext2 = self._count_extended(fs2)
        
        # Two-hand letter recognition
        letter = None
        confidence = 0.75
        
        # Both hands making fist = A or E
        if ext1 == 0 and ext2 == 0:
            letter = 'A'
            confidence = 0.80
        
        # One hand with one finger, other with two = could be various letters
        elif ext1 + ext2 == 3:
            letter = 'W'
            confidence = 0.70
        
        # Both hands with index fingers = could be forming letters
        elif fs1['index'] and fs2['index'] and ext1 == 1 and ext2 == 1:
            # Two index fingers - could be making shapes
            # Check if they're touching or forming a shape
            idx1 = hand1[8]
            idx2 = hand2[8]
            dist = np.sqrt((idx1[0] - idx2[0])**2 + (idx1[1] - idx2[1])**2)
            
            if dist < 50:  # Close together
                letter = 'X'  # Crossed
                confidence = 0.70
            else:
                letter = 'H'  # Parallel
                confidence = 0.65
        
        # V shape with both hands
        elif ext1 == 2 and ext2 == 2:
            if (fs1['index'] and fs1['middle'] and fs2['index'] and fs2['middle']):
                letter = 'W'
                confidence = 0.75
        
        # If no two-hand pattern recognized, use the dominant (first) hand
        if letter is None:
            return self.classify(hand1)
        
        self.current_letter = letter
        self.confidence = confidence
        
        return letter, confidence
