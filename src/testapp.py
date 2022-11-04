import streamlit as st

# Custom imports 
from multipage import MultiPage
from pages import firsttest, boxleague

# Create an instance of the app 
app = MultiPage()

# Title of the main page
#st.title("Club Locker App")
st.set_page_config(
    page_title="Title",
    page_icon="res/nikkiboxi.png",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={}
)

# Add all your applications (pages) here
app.add_page("Box League", boxleague.app)
app.add_page("First Test", firsttest.app)

# The main app
app.run()