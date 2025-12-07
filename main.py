import streamlit as st
import os

os.makedirs('db', exist_ok=True)

st.session_state.logged_in = False
st.session_state.username = None

st.set_page_config(
    layout="centered",
    initial_sidebar_state="collapsed"
)
st.switch_page("pages/login.py")