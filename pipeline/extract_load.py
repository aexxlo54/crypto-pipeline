# ============================================================
# CRYPTO PIPELINE - Extract & Load Script
# This runs automatically every day via GitHub Actions
# Pulls top 10 crypto prices from CoinGecko → loads to Snowflake
# ============================================================

import requests
import snowflake.connector
import os
from datetime import datetime, timezone

# -------------------------------------------------------
# SECTION 1: Get credentials from environment variables
# In GitHub Actions, these come from GitHub Secrets
# (same concept as Colab Secrets, different platform)
# -------------------------------------------------------
account  = os.environ['SNOWFLAKE_ACCOUNT']
user     = os.environ['SNOWFLAKE_USER']
password = os.environ['SNOWFLAKE_PASSWORD']

# -------------------------------------------------------
# SECTION 2: Call the CoinGecko API
# -------------------------------------------------------
url = "https://api.coingecko.com/api/v3/coins/markets"
params = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 10,
    "page": 1
}
response = requests.get(url, params=params)
coins = response.json()
print(f"Fetched {len(coins)} coins from CoinGecko ✅")

# -------------------------------------------------------
# SECTION 3: Connect to Snowflake
# -------------------------------------------------------
conn = snowflake.connector.connect(
    account=account,
    user=user,
    password=password,
    database="CRYPTO_DB",
    warehouse="COMPUTE_WH"
)
cursor = conn.cursor()
print("Connected to Snowflake ✅")

# -------------------------------------------------------
# SECTION 4: Create schema and table if not exists
# -------------------------------------------------------
cursor.execute("CREATE SCHEMA IF NOT EXISTS CRYPTO_DB.RAW")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS CRYPTO_DB.RAW.COIN_PRICES (
        ID VARCHAR,
        NAME VARCHAR,
        SYMBOL VARCHAR,
        CURRENT_PRICE FLOAT,
        MARKET_CAP FLOAT,
        TOTAL_VOLUME FLOAT,
        PRICE_CHANGE_24H FLOAT,
        LOADED_AT TIMESTAMP
    )
""")
print("Schema and table ready ✅")

# -------------------------------------------------------
# SECTION 5: Insert each coin into the table
# -------------------------------------------------------
for coin in coins:
    cursor.execute("""
        INSERT INTO CRYPTO_DB.RAW.COIN_PRICES
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        coin['id'],
        coin['name'],
        coin['symbol'],
        coin['current_price'],
        coin['market_cap'],
        coin['total_volume'],
        coin['price_change_percentage_24h'],
        datetime.now(timezone.utc)
    ))

# -------------------------------------------------------
# SECTION 6: Commit and close
# -------------------------------------------------------
conn.commit()
cursor.close()
conn.close()
print(f"Loaded {len(coins)} rows into CRYPTO_DB.RAW.COIN_PRICES ✅")
