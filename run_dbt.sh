#!/bin/bash
set -e

echo "===== dbt run démarré : $(date) ====="

# Clé privée depuis variable d'environnement AWS Secrets Manager
echo "$SNOWFLAKE_PRIVATE_KEY" > /tmp/rsa_key_new.p8
chmod 600 /tmp/rsa_key_new.p8

# Créer profiles.yml
mkdir -p ~/.dbt
cat > ~/.dbt/profiles.yml << HEREDOC
data_pipeline:
  outputs:
    dev:
      type: snowflake
      account: ${SNOWFLAKE_ACCOUNT}
      user: ${SNOWFLAKE_USER}
      private_key_path: /tmp/rsa_key.p8
      database: ${SNOWFLAKE_DATABASE}
      schema: ${SNOWFLAKE_SCHEMA}
      warehouse: ${SNOWFLAKE_WAREHOUSE}
      role: ${SNOWFLAKE_ROLE}
      threads: 4
      transient: false
  target: dev
HEREDOC

dbt debug
dbt run --select tag:${DBT_TAG}
dbt test --select tag:${DBT_TAG}
dbt docs generate

rm -f /tmp/rsa_key.p8
echo "===== dbt run terminé : $(date) ====="
