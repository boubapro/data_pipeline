#!/bin/bash
set -euo pipefail

AWS_REGION="${AWS_REGION:-eu-west-1}"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_URL="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/dbt-snowflake"

# Chemins
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"  # aws/
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"                      # racine

if [[ -z "${SNOWFLAKE_PRIVATE_KEY_SECRET_ARN:-}" ]]; then
  printf 'Définissez SNOWFLAKE_PRIVATE_KEY_SECRET_ARN (secret PEM dans AWS Secrets Manager).\n' >&2
  exit 1
fi

if [[ ! -r "$PROJECT_ROOT/rsa_key.p8" ]]; then
  printf 'Clé Terraform introuvable : %s/rsa_key.p8\n' "$PROJECT_ROOT" >&2
  exit 1
fi

echo "1. Déployer l'infrastructure"
cd "$SCRIPT_DIR"
terraform init -upgrade
export TF_VAR_aws_region="$AWS_REGION"
# Base/schéma sans valeur par défaut : repris de l'environnement s'il est défini
# (sinon Terraform les lit dans aws/*.tfvars ou échoue explicitement).
[[ -n "${SNOWFLAKE_DATABASE:-}" ]] && export TF_VAR_snowflake_database="$SNOWFLAKE_DATABASE"
[[ -n "${SNOWFLAKE_SCHEMA:-}" ]] && export TF_VAR_snowflake_schema="$SNOWFLAKE_SCHEMA"
export TF_VAR_snowflake_private_key_secret_arn="$SNOWFLAKE_PRIVATE_KEY_SECRET_ARN"
if [[ -n "${SNOWFLAKE_PRIVATE_KEY_PASSPHRASE_SECRET_ARN:-}" ]]; then
  export TF_VAR_snowflake_private_key_passphrase_secret_arn="$SNOWFLAKE_PRIVATE_KEY_PASSPHRASE_SECRET_ARN"
fi
export TF_VAR_snowflake_private_key
TF_VAR_snowflake_private_key="$(cat "$PROJECT_ROOT/rsa_key.p8")"
terraform apply -auto-approve -input=false
unset TF_VAR_snowflake_private_key

echo "2. Build et pousser l'image Docker"
cd "$PROJECT_ROOT"
docker build -t dbt-snowflake .
aws ecr get-login-password --region "$AWS_REGION" | \
  docker login --username AWS --password-stdin "$ECR_URL"
docker tag dbt-snowflake:latest "$ECR_URL:latest"
docker push "$ECR_URL:latest"

echo "Déploiement terminé."
