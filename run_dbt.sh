#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [[ -f .env ]]; then
  set -a
  source .env
  set +a
fi

required_vars=(
  SNOWFLAKE_ACCOUNT
  SNOWFLAKE_USER
  SNOWFLAKE_ROLE
  SNOWFLAKE_WAREHOUSE
  SNOWFLAKE_DATABASE
  SNOWFLAKE_SCHEMA
  SNOWFLAKE_PRIVATE_KEY_PATH
)

for name in "${required_vars[@]}"; do
  if [[ -z "${!name:-}" ]]; then
    printf 'Variable requise absente : %s\n' "$name" >&2
    exit 1
  fi
done

if [[ ! -r "$SNOWFLAKE_PRIVATE_KEY_PATH" ]]; then
  printf 'Fichier de clé privée introuvable ou illisible.\n' >&2
  exit 1
fi

chmod 600 "$SNOWFLAKE_PRIVATE_KEY_PATH"

if [[ -x .venv/bin/dbt ]]; then
  DBT_BIN=.venv/bin/dbt
elif ! DBT_BIN="$(command -v dbt)"; then
  printf 'dbt est introuvable; installez les dépendances ou activez votre environnement virtuel.\n' >&2
  exit 1
fi

DBT_TARGET="${DBT_TARGET:-dev}"
case "$DBT_TARGET" in
  dev|int|prod) ;;
  *)
    printf 'DBT_TARGET doit être dev, int ou prod.\n' >&2
    exit 1
    ;;
esac

dbt_args=(--profiles-dir . --target "$DBT_TARGET")
selector=()
if [[ -n "${DBT_TAG:-}" ]]; then
  selector=(--select "tag:$DBT_TAG")
fi

echo "===== dbt run démarré : $(date) ====="
"$DBT_BIN" debug "${dbt_args[@]}"
"$DBT_BIN" deps
"$DBT_BIN" run "${selector[@]}" "${dbt_args[@]}"
"$DBT_BIN" test "${selector[@]}" "${dbt_args[@]}"
"$DBT_BIN" docs generate
echo "===== dbt run terminé : $(date) ====="
