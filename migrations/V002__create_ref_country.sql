-- migrations/V002__create_ref_country.sql
CREATE TABLE IF NOT EXISTS REF_COUNTRY (
    country_code   VARCHAR(3)    NOT NULL,
    country_name   VARCHAR(100)  NOT NULL,
    region         VARCHAR(50),
    created_at     TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

MERGE INTO REF_COUNTRY AS target
USING (
    SELECT column1 AS country_code, column2 AS country_name, column3 AS region
    FROM VALUES
        ('FR', 'France', 'Europe'),
        ('US', 'United States', 'Americas'),
        ('DE', 'Germany', 'Europe')
) AS source
ON target.country_code = source.country_code
WHEN MATCHED THEN UPDATE SET
    country_name = source.country_name,
    region = source.region
WHEN NOT MATCHED THEN INSERT (country_code, country_name, region)
    VALUES (source.country_code, source.country_name, source.region);
