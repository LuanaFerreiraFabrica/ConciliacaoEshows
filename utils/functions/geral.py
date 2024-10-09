import streamlit as st
import pandas as pd
from workalendar.america import Brazil
from datetime import datetime, timedelta
from utils.queries import *

def config_sidebar():
  st.sidebar.title("Menu")
  st.sidebar.page_link("pages/Conciliacao_EPM.py", label="Conciliação Kamino")
  st.sidebar.page_link("pages/Concliacao_Transfeera.py", label="Conciliação Transfeera")


def format_brazilian(num):
    if pd.isnull(num):
        return None  # Ou np.nan, caso prefira manter como NaN
    return f"{num:,.2f}".replace('.', ',')

def format_columns_brazilian(df, numeric_columns):
  for col in numeric_columns:
    if col in df.columns:
      df[col] = df[col].apply(format_brazilian)
  return df

def format_date_brazilian(df, date_column):
  df[date_column] = pd.to_datetime(df[date_column])
  df[date_column] = df[date_column].dt.strftime('%d-%m-%Y')
  return df


def highlight_values(val):
    color = 'red' if '-' in val else 'green'
    return f'color: {color}'