from sqlalchemy import create_engine
import pandas as pd

# UPDATE WITH YOUR CREDENTIALS
DB_USER = "ahmedhatahet"
DB_PASSWORD = "GalacticTits1!"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "real_estate_db"

DATABASE_URL = f"postgresql://ahmedhatahet:GalacticTits1!@localhost:5432/real_estate_db"

engine = create_engine(DATABASE_URL)


def get_properties():
    query = "SELECT * FROM properties;"
    return pd.read_sql(query, engine)


def get_financials():
    query = "SELECT * FROM financials;"
    return pd.read_sql(query, engine)