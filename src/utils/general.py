import base64

import pandas as pd
import streamlit as st


@st.experimental_memo
def convert_df_to_csv(df_to_convert: pd.DataFrame) -> str:
    return df_to_convert.to_csv().encode("utf-8")


def hide_table_row_index() -> str:
    style_string = """
                <style>
                thead tr th:first-child {display:none}
                tbody th {display:none}
                </style>
                """
    return style_string


def custom_css(background_path: str) -> None:
    with open(background_path, "rb") as image:
        encoded_string = base64.b64encode(image.read())
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=PT+Sans');
		html, body, [class*="css"]  {{
			font-family: 'PT Sans', sans-serif;
		}}

        a {{
            text-decoration: none;
        }}
        
        html {{
            font-size: 110%;
        }}

        [data-testid="stAppViewContainer"] {{
            animation-fill-mode: forwards;
        }}

        @-webkit-keyframes fade-in-scale-down{{
            0% {{
                opacity:0;
                -webkit-transform:scale(1.1);
                -ms-transform:scale(1.1);
                transform:scale(1.1)
            }}
            100% {{
                opacity:1;
                -webkit-transform:scale(1);
                -ms-transform:scale(1);
                transform:scale(1);
            }}
        }}

        [data-testid="stHeader"] {{
            background-color: rgba(0, 0, 0, 0);
        }}

        [data-testid="stSidebar"] {{
            background: radial-gradient(
                rgba(35, 35, 35, 1.0) 8%,
                #181521 8%
            );
            background-position: 0% 0%;
            background-size: 16px 16px;
            height: 100%;
            width: 100%;
        }}

        .block-container {{
            max-width: 66rem;
            padding-bottom: 4vh;
            padding-top: 4vh;
        }}

        blockquote {{
            border-left: 2px solid rgb(130 130 130 / 50%);
        }}

        img {{
            border-radius: 15px;
            border-color: transparent;
            -webkit-transition: all 0.5s linear;
            -o-transition: all 0.5s linear;
            transition: all 0.5s linear;
            animation: fadeInOpacity 4s;
        }}

        @-webkit-keyframes fadeInOpacity {{
            0% {{ opacity: 0; }}
            100% {{ opacity: 1; }}
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

        [data-testid="stAppViewContainer"] > .main {{
            background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
            background-size: cover;
            background-attachment: local;
            background-position: 66%;
            animation-name: fadeInBackground;
            animation-duration 4s;
            animation-fill-mode: forwards;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def caption_text(name: str, text: str) -> str:
    return f"<p style='text-align: center; color: #d4d4d4; font-size: 0.8em;'><strong>{name}</strong>   {text}</p>"


def color_covid(v: str) -> str:
    if v == "pre":
        return "color: #daaa4c;"
    elif v == "post":
        return "color: #a7003c;"
    else:
        return ""
