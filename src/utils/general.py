import base64
import pandas as pd
import streamlit as st


@st.experimental_memo
def convert_df_to_csv(df_to_convert: pd.DataFrame) -> str:
    return df_to_convert.to_csv().encode("utf-8")


def add_bg_from_local(image_file: str) -> None:
    with open(image_file, "rb") as image:
        encoded_string = base64.b64encode(image.read())
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
    .block-container {{
        max-width: 60rem;
    }}
    img {{
        border-radius: 15px;
        -webkit-filter: drop-shadow(0px 0px 0px rgba(255,255,255,0.80));
        -webkit-transition: all 0.5s linear;
        -o-transition: all 0.5s linear;
        transition: all 0.5s linear;
    }}
    img:hover {{
	    -webkit-filter: drop-shadow(0px 0px 5px rgba(188, 146, 67, 0.8));
    }}
    button[title="View fullscreen"] {{
        display: none;
    }}
    </style>
    """,
        unsafe_allow_html=True,
    )
