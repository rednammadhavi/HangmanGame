import streamlit as st
import random
from PIL import Image
import os

# --- Load hangman images ---
# Ensure the 'images' folder exists and contains the required images.
image_folder = "images"
if not os.path.exists(image_folder):
    st.error("The 'images' folder is missing. Please create it and add the hangman images.")
    st.stop()
    
try:
    hangman_images = [Image.open(os.path.join(image_folder, f"hangman_stage_{i}.png")) for i in range(7)]
except FileNotFoundError:
    st.error("Could not find all hangman images (hangman_stage_0.png to hangman_stage_6.png) in the 'images' folder.")
    st.stop()


# --- Word categories ---
word_categories = {
    "Animals": ["elephant", "giraffe", "kangaroo", "dolphin", "tiger", "penguin"],
    "Programming": ["python", "javascript", "hangman", "developer", "function", "variable"],
    "Fruits": ["banana", "strawberry", "mango", "apple", "pineapple", "grapes"]
}

# --- Initialize session state ---
if "word" not in st.session_state:
    category = random.choice(list(word_categories.keys()))
    st.session_state.word = random.choice(word_categories[category])
    st.session_state.category = category
    st.session_state.guessed_letters = set()
    st.session_state.wrong_guesses = 0
    st.session_state.max_attempts = len(hangman_images) - 1
    st.session_state.game_over = False
    st.session_state.message = ""

# --- Display word ---
def display_word(word, guessed_letters):
    displayed = ""
    for letter in word:
        if letter in guessed_letters:
            # <-- CHANGE: Slightly reduced font size for the word to prevent wrapping and save space
            displayed += f"<span style='color:#4caf50;font-weight:bold;font-size:2.2rem'>{letter.upper()}</span> "
        else:
            displayed += "<span style='font-size:2.2rem'>_</span> "
    return displayed.strip()

# --- Page Config ---
st.set_page_config(page_title="🎮 Hangman Game", layout="wide")

# --- Heading ---
st.markdown("<h1 style='text-align:center; color:#ff5722;'>🎮 Hangman Game</h1>", unsafe_allow_html=True)

# --- Two equal columns for info and image ---
col_info, col_img = st.columns([1, 1])

# --- Info Column ---
with col_info:
    st.markdown(
        f"""
        <div style='font-size:1.1rem; line-height:1.6;'>
            <b>Category:</b> {st.session_state.category}<br>
            <b>Guessed letters:</b> {', '.join(sorted(st.session_state.guessed_letters)).upper() if st.session_state.guessed_letters else 'None'}<br>
            <b>Chances left:</b> {st.session_state.max_attempts - st.session_state.wrong_guesses}
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        f"<div style='margin-top:20px;'>{display_word(st.session_state.word, st.session_state.guessed_letters)}</div>",
        unsafe_allow_html=True
    )

# --- Image Column ---
with col_img:
    st.image(hangman_images[st.session_state.wrong_guesses], use_container_width=True)

    
# --- Container for input and keyboard to group them ---
with st.container():
    # --- User input ---
    # Centering the text input for better alignment with the keyboard
    st.markdown("""
        <style>
            .stTextInput {
                width: 70%;
                margin: 0 auto;
            }
        </style>
    """, unsafe_allow_html=True)
    user_input = st.text_input("Type a letter and press Enter:", max_chars=1, key="letter_input").lower()


    # --- Win / Loss check ---
if not st.session_state.game_over:
    if all(l in st.session_state.guessed_letters for l in st.session_state.word):
        st.session_state.message = f"🎉 You won! The word was: **{st.session_state.word.upper()}**"
        st.session_state.game_over = True
        st.rerun()
    elif st.session_state.wrong_guesses >= st.session_state.max_attempts:
        st.session_state.message = f"💀 Game Over! The word was: **{st.session_state.word.upper()}**"
        st.session_state.game_over = True
        st.rerun()

    if user_input and user_input.isalpha() and user_input not in st.session_state.guessed_letters:
        st.session_state.guessed_letters.add(user_input)
        if user_input not in st.session_state.word:
            st.session_state.wrong_guesses += 1
        # Rerun to clear the input box after submission
        st.rerun()

    # --- Keyboard Section ---
    keyboard_rows = ["qwertyuiop", "asdfghjkl", "zxcvbnm"]
    # <-- CHANGE: Reduced margin-top from 30px to 15px
    st.markdown("<div style='text-align:center; margin-top:15px;'>", unsafe_allow_html=True)
    for row in keyboard_rows:
        row_html = ""
        for letter in row:
            # Buttons are grayed out if the letter has been guessed
            is_guessed = letter in st.session_state.guessed_letters
            color = "#9e9e9e" if is_guessed else "#03a9f4" # Gray if guessed, blue otherwise
            row_html += f"<button style='width:45px; height:45px; margin:3px; border-radius:8px; border:none; background-color:{color}; color:white; font-weight:bold; font-size:16px;'>{letter.upper()}</button>"
        st.markdown(f"<div style='display:flex; justify-content:center; flex-wrap:wrap;'>{row_html}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# --- Reset / Replay Buttons (only show when game is over) ---
if st.session_state.game_over:
    st.markdown(f"<h3 style='text-align:center; color:#ff5722; margin-top: 20px;'>{st.session_state.message}</h3>", unsafe_allow_html=True)
    
    # Use columns to center the buttons nicely
    _, col_btn1, col_btn2, _ = st.columns([1,1,1,1])
    with col_btn1:
        if st.button("▶️ Play Again", use_container_width=True):
            # Keep the same category logic but pick a new word
            category = st.session_state.category
            new_word = random.choice(word_categories[category])
            
            # Reset all game state variables
            st.session_state.word = new_word
            st.session_state.guessed_letters = set()
            st.session_state.wrong_guesses = 0
            st.session_state.game_over = False
            st.session_state.message = ""
            st.rerun()
    with col_btn2:
        if st.button("🔄 New Game", use_container_width=True):
            # Clears everything to start fresh with a new category
            st.session_state.clear()
            st.rerun()