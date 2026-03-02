import streamlit as st
from sqlalchemy import create_engine
import pandas as pd

host = st.secrets["database"]["host"]
dbname = st.secrets["database"]["dbname"]
user = st.secrets["database"]["user"]
password = st.secrets["database"]["password"]
sslmode = st.secrets["database"]["sslmode"]

DATABASE_URL = f"postgresql://{user}:{password}@{host}/{dbname}?sslmode={sslmode}"

engine = create_engine(DATABASE_URL)

def get_properties():
    query = "SELECT * FROM properties;"
    return pd.read_sql(query, engine)

def get_financials():
    query = "SELECT * FROM financials;"
    return pd.read_sql(query, engine)