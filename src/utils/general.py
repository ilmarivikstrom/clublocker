import streamlit as st


@st.experimental_memo
def convert_df_to_csv(df):
    return df.to_csv().encode("utf-8")
