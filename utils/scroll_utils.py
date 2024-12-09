import streamlit as st
from pathlib import Path

def scroll_to_top():
    """
    Inject JavaScript to scroll to the top of the page.
    Uses a separate HTML file to ensure proper loading and execution.
    """
    scroll_html = Path('assets/scroll.html').read_text()
    st.components.v1.html(scroll_html, height=0)
