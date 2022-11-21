import base64
import streamlit as st


@st.experimental_memo
def convert_df_to_csv(df):
    return df.to_csv().encode("utf-8")


def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover
    }}
    [data-testid="stHeader"] {{
        background-color: rgba(0, 0, 0, 0);
    }}
    [data-testid="stSidebar"] {{
        background: #232526;
        background: linear-gradient(to up, #414345, #232526);
    }}
    img {{
        border-radius: 15px;
    }}
    </style>
    """,
    unsafe_allow_html=True
    )