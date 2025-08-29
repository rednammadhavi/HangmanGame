import streamlit as st
import random
from PIL import Image
import os
import base64
from io import BytesIO
from words import word_categories  # Import words from words.py

# --- Page Config ---
st.set_page_config(page_title="🎮 Hangman Game", layout="wide")

# --- Load CSS ---
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

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

# --- Encode PIL image to base64 ---
def pil_to_base64(img):
    buf = BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

# --- Initialize Session State ---
if "word" not in st.session_state:
    category = random.choice(list(word_categories.keys()))
    selected = random.choice(word_categories[category])
    st.session_state.word = selected["word"]
    st.session_state.hint = selected["hint"]
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
col_left, col_right = st.columns([1, 2], gap="medium")

with col_left:
    img_base64 = pil_to_base64(hangman_images[st.session_state.wrong_guesses])
    st.markdown(f'<img src="data:image/png;base64,{img_base64}" style="width:100%; pointer-events:none;">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class='game-info'>
        <b>Category:</b> {st.session_state.category}<br>
        <b>Guessed Letters:</b> {', '.join(sorted(st.session_state.guessed_letters)).upper() if st.session_state.guessed_letters else 'None'}<br>
        <b>Chances Left:</b> <span style='color:#ff5722; font-weight:bold;'>{st.session_state.max_attempts - st.session_state.wrong_guesses}</span>
    </div>
    {display_word(st.session_state.word, st.session_state.guessed_letters)}
    <div style="text-align:center; margin:5px 0; font-style:italic; color:#555;">
        Hint: {st.session_state.hint}
    </div>
""", unsafe_allow_html=True)


with col_right:
    if not st.session_state.game_over:
        user_input = st.text_input("Type a letter:", max_chars=1, key="letter_input", placeholder="Guess a letter").lower()
        if user_input and user_input.isalpha() and user_input not in st.session_state.guessed_letters:
            st.session_state.guessed_letters.add(user_input)
            if user_input not in st.session_state.word:
                st.session_state.wrong_guesses += 1
            st.rerun()

        st.markdown("<h4 style='text-align:center;'>Or Click a Letter</h4>", unsafe_allow_html=True)
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

        reset_col1, reset_col2, reset_col3 = st.columns([1, 2, 1])
        with reset_col2:
            if st.button("🔄 Reset Game", key="reset_btn", use_container_width=True):
                selected = random.choice(word_categories[st.session_state.category])
                st.session_state.word = selected["word"]
                st.session_state.hint = selected["hint"]
                st.session_state.guessed_letters = set()
                st.session_state.wrong_guesses = 0
                st.session_state.game_over = False
                st.session_state.message = ""
                st.rerun()
    else:
        st.markdown(f"<div class='final-message'>{st.session_state.message}</div>", unsafe_allow_html=True)
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("▶️ Play Again", key="play_again", use_container_width=True):
                selected = random.choice(word_categories[st.session_state.category])
                st.session_state.word = selected["word"]
                st.session_state.hint = selected["hint"]
                st.session_state.guessed_letters = set()
                st.session_state.wrong_guesses = 0
                st.session_state.game_over = False
                st.session_state.message = ""
                st.rerun()
        with btn_col2:
            if st.button("🔄 New Game", key="new_game", use_container_width=True):
                st.session_state.clear()
                st.rerun()

# --- Check Win/Loss ---
if not st.session_state.game_over:
    if all(letter in st.session_state.guessed_letters for letter in st.session_state.word):
        st.session_state.message = f"🎉 You won! The word was: **{st.session_state.word.upper()}**"
        st.session_state.game_over = True
        st.rerun()
    elif st.session_state.wrong_guesses >= st.session_state.max_attempts:
        st.session_state.message = f"💀 Game Over! The word was: **{st.session_state.word.upper()}**"
        st.session_state.game_over = True
        st.rerun()
