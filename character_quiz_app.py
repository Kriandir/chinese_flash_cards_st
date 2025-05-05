#!/usr/bin/env python3
"""
Streamlit Chinese Character Quiz – Reliable Color & Auto‑Advance
================================================================
Press **Enter** → the Hanzi flashes vivid green/red for one full second,
then the next card appears automatically.

Key points
----------
* Uses `response_checked` + `timer_start` flags in `st.session_state` to
  control the delay cleanly.
* No JavaScript needed; a tiny `time.sleep(0.1)` loop plus
  `st.rerun()` keeps the UI responsive.
* **Stop** ends early; **Restart** after completion.

Run:
    streamlit run character_quiz_app.py
"""

import json
import random
import time
from pathlib import Path

import streamlit as st

DATA_FILE = Path(__file__).with_name("characters.json")
BRIGHT_GREEN = "#00c853"
BRIGHT_RED = "#ff1744"


# ---------- Load deck ----------
@st.cache_data
def load_deck(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def normalize(ans: str) -> str:
    return ans.lower().replace(" ", "")



# ---------- Render helper ----------
BOX_TEMPLATE = """
<div style="width:300px;height:300px;border:2px solid #ddd;margin:auto;
            display:flex;align-items:center;justify-content:center;">
  <span style="font-size:200px;line-height:1;color:{color};">
    {char}
  </span>
</div>
"""
box = st.empty()
feedback = st.empty()
def render(char: str, color: str):
    with box.container():
        st.markdown(BOX_TEMPLATE.format(char=char, color=color), unsafe_allow_html=True)
# ---------- Callbacks ----------
    with feedback.container():
        st.write(st.session_state.feedback)
def evaluate_answer():
    card = st.session_state.deck[st.session_state.idx]
    correct_en = card["english"]
    given = st.session_state.answer

    st.session_state.response_checked = True
    st.session_state.timer_start = time.time()
    st.session_state.correct = normalize(given) == normalize(correct_en)

    if st.session_state.correct:
        st.session_state.score += 1
        st.session_state.feedback = "✅ Correct!"
    else:
        st.session_state.feedback = f"❌ Wrong. Correct: {correct_en}"


    char_color = BRIGHT_GREEN if st.session_state.correct else BRIGHT_RED
    render(card["hanzi"], char_color)
    if "Wrong" in st.session_state.feedback:
        time.sleep(1.4)
    else:
        time.sleep(1.4)
def advance_card():
    st.session_state.idx += 1
    st.session_state.answer = ""
    st.session_state.response_checked = False
    st.session_state.feedback = ""
    st.session_state.correct = None
    st.session_state.pop("timer_start", None)


# ---------- Session state init ----------
if "deck" not in st.session_state:
    st.session_state.deck = load_deck(DATA_FILE)
    random.shuffle(st.session_state.deck)
    st.session_state.idx = 0
    st.session_state.score = 0
    st.session_state.answer = ""
    st.session_state.response_checked = False
    st.session_state.correct = None
    st.session_state.feedback = ""

# ---------- Auto‑advance after 1 s ----------
if st.session_state.response_checked and "timer_start" in st.session_state:
    elapsed = time.time() - st.session_state.timer_start
    if elapsed >= 1:
        advance_card()
    else:
        # brief pause then rerun so timer keeps counting without blocking long
        time.sleep(0.1)
        st.rerun()


# ---------- Stop button ----------
col_stop, _ = st.columns([1, 9])
if col_stop.button("Stop"):
    st.session_state.idx = len(st.session_state.deck)

# ---------- End quiz ----------
if st.session_state.idx >= len(st.session_state.deck):
    st.success(
        f"Finished! Your score: {st.session_state.score}/{len(st.session_state.deck)} "
        f"({st.session_state.score/len(st.session_state.deck)*100:.0f}%)"
    )
    if st.button("Restart"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
    st.stop()

card = st.session_state.deck[st.session_state.idx]

# ---------- Determine color ----------
char_color = "#000"  # default black

# ---------- Display Hanzi ----------
def display_hanzi(char_color):
    st.markdown(
        f"""<div style='text-align:center; font-size: 200px; line-height:1; color:{char_color};'>
            {card['hanzi']}
        </div>""",
        unsafe_allow_html=True,
    )
if not st.session_state.response_checked:
    card = st.session_state.deck[st.session_state.idx]
    render(card["hanzi"], "#FFFFFF")

# ---------- Input ----------
st.text_input(
    "English meaning:",
    key="answer",
    on_change=evaluate_answer,
    disabled=st.session_state.response_checked,
    placeholder="Type meaning and press Enter…",
)

