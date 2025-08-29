import streamlit as st
import random
from PIL import Image
import os

# --- Page Config ---
st.set_page_config(page_title="🎮 Hangman Game", layout="wide")

# --- Custom CSS for styling ---
st.markdown("""
<style>
/* Main container spacing */
.main .block-container { padding: 1rem; }

/* Reduce vertical gap */
div[data-testid="stVerticalBlock"] { gap: 0.8rem; }

/* Game info box */
.game-info {
    font-size: 1rem;
    line-height: 1.5;
    background-color: #f0f2f6;
    padding: 15px;
    border-radius: 10px;
    border: 2px solid #ddd;
}

/* Word display */
.word-display span {
    font-size: 2.5rem;
    margin: 0 0.2rem;
}

/* Keyboard buttons */
div[data-testid="stButton"] button {
    font-size: 1.1rem;
    font-weight: bold;
    height: 3rem;
    border-radius: 8px;
}

/* Keyboard container center */
.keyboard-row { display: flex; justify-content: center; margin-bottom: 0.5rem; }

/* Final message */
.final-message {
    font-size: 1.5rem;
    font-weight: bold;
    text-align: center;
    margin-top: 20px;
}

/* Reset button */
.reset-btn {
    background-color: #ff9800 !important;
    color: white !important;
    margin-top: 15px;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .word-display span { font-size: 2rem; }
    div[data-testid="stButton"] button { height: 2.5rem; font-size: 1rem; }
}
</style>
""", unsafe_allow_html=True)

# --- Load Hangman Images ---
image_folder = "images"
if not os.path.exists(image_folder):
    st.error("The 'images' folder is missing. Add hangman_stage_0.png to hangman_stage_6.png.")
    st.stop()

try:
    hangman_images = [Image.open(os.path.join(image_folder, f"hangman_stage_{i}.png")) for i in range(7)]
except FileNotFoundError:
    st.error("Missing hangman images in 'images' folder.")
    st.stop()

# --- Word Categories ---
word_categories = {
    "Animals": ["elephant", "giraffe", "kangaroo", "dolphin", "tiger", "penguin"],
    "Programming": ["python", "javascript", "hangman", "developer", "function", "variable"],
    "Fruits": ["banana", "strawberry", "mango", "apple", "pineapple", "grapes"]
}

# --- Initialize Session State ---
if "word" not in st.session_state:
    category = random.choice(list(word_categories.keys()))
    st.session_state.word = random.choice(word_categories[category])
    st.session_state.category = category
    st.session_state.guessed_letters = set()
    st.session_state.wrong_guesses = 0
    st.session_state.max_attempts = len(hangman_images) - 1
    st.session_state.game_over = False
    st.session_state.message = ""

# --- Display Word Function ---
def display_word(word, guessed_letters):
    displayed = ""
    for letter in word:
        if letter in guessed_letters:
            displayed += f"<span style='color:#4caf50;font-weight:bold;'>{letter.upper()}</span>"
        else:
            displayed += "<span style='color:#333;'>_</span>"
    return f"<div class='word-display' style='text-align:center; margin:10px 0;'>{displayed}</div>"

# --- Header ---
st.markdown("<h1 style='text-align:center; color:#ff5722;'>🎮 Hangman Game</h1>", unsafe_allow_html=True)

# --- Main Layout ---
col_left, col_right = st.columns([1, 2], gap="large")

# --- Left Column: Images + Info ---
with col_left:
    st.image(hangman_images[st.session_state.wrong_guesses], use_container_width=True)
    st.markdown(f"""
        <div class='game-info'>
            <b>Category:</b> {st.session_state.category}<br>
            <b>Guessed Letters:</b> {', '.join(sorted(st.session_state.guessed_letters)).upper() if st.session_state.guessed_letters else 'None'}<br>
            <b>Chances Left:</b> <span style='color:#ff5722; font-weight:bold;'>{st.session_state.max_attempts - st.session_state.wrong_guesses}</span>
        </div>
        {display_word(st.session_state.word, st.session_state.guessed_letters)}
    """, unsafe_allow_html=True)

# --- Right Column: Input + Keyboard + Reset ---
with col_right:
    if not st.session_state.game_over:
        # User text input
        user_input = st.text_input("Type a letter:", max_chars=1, key="letter_input", placeholder="Guess a letter").lower()
        if user_input and user_input.isalpha() and user_input not in st.session_state.guessed_letters:
            st.session_state.guessed_letters.add(user_input)
            if user_input not in st.session_state.word:
                st.session_state.wrong_guesses += 1
            st.rerun()
        
        st.markdown("<h4 style='text-align:center;'>Or Click a Letter</h4>", unsafe_allow_html=True)
        
        # On-screen keyboard
        keyboard_rows = ["qwertyuiop", "asdfghjkl", "zxcvbnm"]
        for row in keyboard_rows:
            cols = st.columns(len(row))
            for i, letter in enumerate(row):
                with cols[i]:
                    is_guessed = letter in st.session_state.guessed_letters
                    if st.button(letter.upper(), key=f"kb_{letter}", use_container_width=True, disabled=is_guessed):
                        st.session_state.guessed_letters.add(letter)
                        if letter not in st.session_state.word:
                            st.session_state.wrong_guesses += 1
                        st.rerun()
        
        # Reset button
        reset_col1, reset_col2, reset_col3 = st.columns([1, 2, 1])
        with reset_col2:
            if st.button("🔄 Reset Game", key="reset_btn", use_container_width=True):
                category = st.session_state.category
                new_word = random.choice(word_categories[category])
                st.session_state.word = new_word
                st.session_state.guessed_letters = set()
                st.session_state.wrong_guesses = 0
                st.session_state.game_over = False
                st.session_state.message = ""
                st.rerun()

# --- Check for Win/Loss ---
if not st.session_state.game_over:
    if all(letter in st.session_state.guessed_letters for letter in st.session_state.word):
        st.session_state.message = f"🎉 You won! The word was: **{st.session_state.word.upper()}**"
        st.session_state.game_over = True
        st.rerun()
    elif st.session_state.wrong_guesses >= st.session_state.max_attempts:
        st.session_state.message = f"💀 Game Over! The word was: **{st.session_state.word.upper()}**"
        st.session_state.game_over = True
        st.rerun()

# --- Game Over Message + Replay ---
if st.session_state.game_over:
    st.markdown(f"<div class='final-message'>{st.session_state.message}</div>", unsafe_allow_html=True)
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("▶️ Play Again", use_container_width=True):
            category = st.session_state.category
            new_word = random.choice(word_categories[category])
            st.session_state.word = new_word
            st.session_state.guessed_letters = set()
            st.session_state.wrong_guesses = 0
            st.session_state.game_over = False
            st.session_state.message = ""
            st.rerun()
    with btn_col2:
        if st.button("🔄 New Game", use_container_width=True):
            st.session_state.clear()
            st.rerun()
