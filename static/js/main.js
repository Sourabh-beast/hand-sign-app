/**
 * Hand Sign Recognition App - Main JavaScript
 * Handles real-time updates, notepad interaction, and UI state
 */

// DOM Elements
const currentLetterEl = document.getElementById('current-letter');
const confidenceFillEl = document.getElementById('confidence-fill');
const confidenceTextEl = document.getElementById('confidence-text');
const notepadTextEl = document.getElementById('notepad-text');
const detectionStatusEl = document.getElementById('detection-status');

const btnSpace = document.getElementById('btn-space');
const btnNewline = document.getElementById('btn-newline');
const btnBackspace = document.getElementById('btn-backspace');
const btnClear = document.getElementById('btn-clear');

// State
let lastLetter = null;
let updateInterval = null;

/**
 * Update the detected letter display
 */
function updateLetterDisplay(letter, confidence) {
    if (letter) {
        currentLetterEl.textContent = letter;
        currentLetterEl.classList.add('detected');
        setTimeout(() => currentLetterEl.classList.remove('detected'), 300);
        
        confidenceFillEl.style.width = `${confidence * 100}%`;
        confidenceTextEl.textContent = `Confidence: ${Math.round(confidence * 100)}%`;
        
        detectionStatusEl.innerHTML = '<span class="status-dot"></span><span>Hand detected</span>';
    } else {
        currentLetterEl.textContent = '-';
        confidenceFillEl.style.width = '0%';
        confidenceTextEl.textContent = 'Waiting for hand...';
        
        detectionStatusEl.innerHTML = '<span class="status-dot" style="background: #f59e0b;"></span><span>No hand detected</span>';
    }
}

/**
 * Update the notepad display
 */
function updateNotepadDisplay(text) {
    notepadTextEl.textContent = text || '';
}

/**
 * Fetch current letter from server
 */
async function fetchLetter() {
    try {
        const response = await fetch('/get_letter');
        const data = await response.json();
        
        if (data.letter !== lastLetter) {
            updateLetterDisplay(data.letter, data.confidence);
            lastLetter = data.letter;
        }
    } catch (error) {
        console.error('Error fetching letter:', error);
    }
}

/**
 * Fetch current notepad text from server
 */
async function fetchNotepad() {
    try {
        const response = await fetch('/get_notepad');
        const data = await response.json();
        updateNotepadDisplay(data.text);
    } catch (error) {
        console.error('Error fetching notepad:', error);
    }
}

/**
 * Clear notepad
 */
async function clearNotepad() {
    try {
        await fetch('/clear_notepad', { method: 'POST' });
        updateNotepadDisplay('');
    } catch (error) {
        console.error('Error clearing notepad:', error);
    }
}

/**
 * Backspace - remove last character
 */
async function backspace() {
    try {
        const response = await fetch('/backspace', { method: 'POST' });
        const data = await response.json();
        updateNotepadDisplay(data.text);
    } catch (error) {
        console.error('Error performing backspace:', error);
    }
}

/**
 * Add space to notepad
 */
async function addSpace() {
    try {
        const response = await fetch('/add_space', { method: 'POST' });
        const data = await response.json();
        updateNotepadDisplay(data.text);
    } catch (error) {
        console.error('Error adding space:', error);
    }
}

/**
 * Add newline to notepad
 */
async function addNewline() {
    try {
        const response = await fetch('/add_newline', { method: 'POST' });
        const data = await response.json();
        updateNotepadDisplay(data.text);
    } catch (error) {
        console.error('Error adding newline:', error);
    }
}

/**
 * Start periodic updates
 */
function startUpdates() {
    // Update letter every 100ms
    updateInterval = setInterval(() => {
        fetchLetter();
        fetchNotepad();
    }, 100);
}

/**
 * Initialize the application
 */
function init() {
    // Bind button events
    btnSpace.addEventListener('click', addSpace);
    btnNewline.addEventListener('click', addNewline);
    btnBackspace.addEventListener('click', backspace);
    btnClear.addEventListener('click', () => {
        if (confirm('Are you sure you want to clear all text?')) {
            clearNotepad();
        }
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.key === ' ' && e.target === document.body) {
            e.preventDefault();
            addSpace();
        } else if (e.key === 'Enter' && e.target === document.body) {
            e.preventDefault();
            addNewline();
        } else if (e.key === 'Backspace' && e.target === document.body) {
            e.preventDefault();
            backspace();
        } else if (e.key === 'Delete' && e.ctrlKey) {
            clearNotepad();
        }
    });
    
    // Start polling for updates
    startUpdates();
    
    console.log('Hand Sign Recognition App initialized');
    console.log('Keyboard shortcuts: Space, Enter, Backspace, Ctrl+Delete to clear');
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', init);
