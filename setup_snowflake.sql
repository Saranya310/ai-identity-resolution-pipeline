-- =====================================================================
-- SNOWFLAKE PRODUCTION ENVIRONMENT SETUP (DDL)
-- Tracks incoming messy customer records and automates resolution triggers
-- =====================================================================

-- 1. Create the ingestion landing table for messy customer data
CREATE OR REPLACE TABLE raw_consumer_ingestion (
    record_id VARCHAR,
    customer_name VARCHAR,
    phone_number VARCHAR,
    email_address VARCHAR,
    zip_code VARCHAR,
    ingested_at TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);

-- 2. Provision the Change Data Capture (CDC) Stream 
-- This silently logs whenever new rows land or change in our ingestion asset
CREATE OR REPLACE STREAM raw_consumer_stream 
ON TABLE raw_consumer_ingestion;

-- 3. Provision an Automated Task scheduled to awake every hour 
-- The WHEN clause evaluates warehouse cost parameters: it sleeps unless data exists
CREATE OR REPLACE TASK process_identity_resolution_task
WAREHOUSE = compute_wh
SCHEDULE = 'USING CRON 0 * * * * UTC' -- Hourly cadence
WHEN SYSTEM$STREAM_HAS_DATA('raw_consumer_stream')
AS
CALL pr_execute_identity_resolution_pipeline();
