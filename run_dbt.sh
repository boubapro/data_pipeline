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
)

for name in "${required_vars[@]}"; do
  if [[ -z "${!name:-}" ]]; then
    printf 'Variable requise absente : %s\n' "$name" >&2
    exit 1
  fi
done

generated_key_path=
if [[ -z "${SNOWFLAKE_PRIVATE_KEY_PATH:-}" && -n "${SNOWFLAKE_PRIVATE_KEY:-}" ]]; then
  umask 077
  SNOWFLAKE_PRIVATE_KEY_PATH="$(mktemp /tmp/snowflake-rsa.XXXXXX)"
  printf '%s' "$SNOWFLAKE_PRIVATE_KEY" > "$SNOWFLAKE_PRIVATE_KEY_PATH"
  export SNOWFLAKE_PRIVATE_KEY_PATH
  generated_key_path="$SNOWFLAKE_PRIVATE_KEY_PATH"
fi

if [[ -z "${SNOWFLAKE_PRIVATE_KEY_PATH:-}" ]]; then
  printf 'Définissez SNOWFLAKE_PRIVATE_KEY_PATH ou SNOWFLAKE_PRIVATE_KEY.\n' >&2
  exit 1
fi

if [[ ! -r "$SNOWFLAKE_PRIVATE_KEY_PATH" ]]; then
  printf 'Fichier de clé privée introuvable ou illisible.\n' >&2
  exit 1
fi

chmod 600 "$SNOWFLAKE_PRIVATE_KEY_PATH"

profile_dir="$(mktemp -d /tmp/dbt-profiles.XXXXXX)"
cleanup() {
  if [[ -n "$generated_key_path" ]]; then
    rm -f "$generated_key_path"
  fi
  rm -f "$profile_dir/profiles.yml" "$profile_dir/.user.yml"
  rmdir "$profile_dir"
}
trap cleanup EXIT

if [[ -x .venv/bin/dbt ]]; then
  DBT_BIN=.venv/bin/dbt
elif ! DBT_BIN="$(command -v dbt)"; then
  printf 'dbt est introuvable; installez les dépendances ou activez votre environnement virtuel.\n' >&2
  exit 1
fi

if [[ -x .venv/bin/python ]]; then
  PYTHON_BIN=.venv/bin/python
elif ! PYTHON_BIN="$(command -v python3)"; then
  printf 'Python 3 est introuvable.\n' >&2
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

"$PYTHON_BIN" scripts/write_dbt_profile.py "$profile_dir"
dbt_args=(--profiles-dir "$profile_dir" --target "$DBT_TARGET")
selector=()
if [[ -n "${DBT_TAG:-}" ]]; then
  selector=(--select "tag:$DBT_TAG")
fi

echo "===== dbt run démarré : $(date) ====="
"$DBT_BIN" debug "${dbt_args[@]}"
"$DBT_BIN" deps --profiles-dir "$profile_dir"
"$DBT_BIN" run "${selector[@]}" "${dbt_args[@]}"
"$DBT_BIN" test "${selector[@]}" "${dbt_args[@]}"
"$DBT_BIN" docs generate
echo "===== dbt run terminé : $(date) ====="
