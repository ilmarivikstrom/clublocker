import base64
import pandas as pd
import streamlit as st


@st.experimental_memo
def convert_df_to_csv(df_to_convert: pd.DataFrame) -> str:
    return df_to_convert.to_csv().encode("utf-8")


def hide_table_row_index():
    hide_table_row_index = """
                <style>
                thead tr th:first-child {display:none}
                tbody th {display:none}
                </style>
                """
    return hide_table_row_index


def custom_css() -> None:
    with open("res/neon_court.png", "rb") as image:
        encoded_string = base64.b64encode(image.read())
    st.markdown(
        f"""
    <style>
    a {{
        text-decoration: none;
    }}
    html {{
        font-size: 110%;
    }}
    [data-testid="stAppViewContainer"] > .main {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover;
        background-attachment: local;
    }}
    [data-testid="stHeader"] {{
        background-color: rgba(0, 0, 0, 0);
    }}
    [data-testid="stSidebar"] {{
        background: #232526;
        background: linear-gradient(to up, #414345, #232526);
    }}
    .block-container {{
        max-width: 66rem;
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
    td {{
        background: #111111bb;
    }}
    th {{
        background: #000000bb;
    }}
    footer {{
        visibility: hidden;
    }}
    #MainMenu {{
        visibility: hidden;
    }}
    footer:after {{
        visibility: visible;
        content: "Ilmari Vikström - 2022";
    }}
    </style>
    """,
        unsafe_allow_html=True,
    )

def caption_text(name, text):
    return f"<p style='text-align: center; color: #d4d4d4; font-size: 0.8em;'><strong>{name}</strong>   {text}</p>"
