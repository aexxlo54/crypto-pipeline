-- ============================================================
-- MODEL: coin_prices_clean
-- Takes raw crypto data from Snowflake and cleans it up
-- Filters out stablecoins, rounds prices, adds readable date
-- ============================================================

-- This tells dbt to create this as a table in Snowflake
{{ config(materialized='table') }}

SELECT
    id,
    name,
    symbol,

    -- Round price to 2 decimal places for readability
    ROUND(current_price, 2)         AS current_price_usd,

    -- Convert large numbers to millions for easier reading
    ROUND(market_cap / 1000000, 2)  AS market_cap_millions,

    -- Round volume to 2 decimal places
    ROUND(total_volume, 2)          AS total_volume_usd,

    -- Round 24h price change to 2 decimal places
    ROUND(price_change_24h, 2)      AS price_change_24h_pct,

    -- Extract just the date from the timestamp
    DATE(loaded_at)                 AS loaded_date,

    -- Keep the full timestamp as well
    loaded_at

FROM CRYPTO_DB.RAW.COIN_PRICES

-- Filter out stablecoins — their price never changes so not interesting
WHERE symbol NOT IN ('usdt', 'usdc', 'busd', 'dai')