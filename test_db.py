from database.db_connection import get_properties, get_financials

print("Fetching Properties...")
properties = get_properties()
print(properties.head())

print("\nFetching Financials...")
financials = get_financials()
print(financials.head())