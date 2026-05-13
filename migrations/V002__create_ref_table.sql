-- migrations/V002__create_ref_country.sql
-- Ce fichier sera exécuté UNE SEULE FOIS au déploiement.
-- Ne jamais modifier ce fichier après déploiement .

CREATE TABLE IF NOT EXISTS REF_COUNTRY (
    country_code   VARCHAR(3)    NOT NULL,
    country_name   VARCHAR(100)  NOT NULL,
    region         VARCHAR(50),
    created_at     TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

INSERT INTO REF_COUNTRY (country_code, country_name, region)
VALUES
    ('FR', 'France',        'Europe'),
    ('US', 'United States', 'Americas'),
    ('DE', 'Germany',       'Europe');
