import streamlit as st
from dotenv import load_dotenv

# Function to load environment variables
def load_environment():
    load_dotenv()

# Function to load custom CSS
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
