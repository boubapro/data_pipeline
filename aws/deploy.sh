#!/bin/bash
set -e

AWS_REGION="eu-west-1"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_URL="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/dbt-snowflake"

# Chemins
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"  # aws/
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"                      # racine

echo "1. Build image Docker"
cd "$PROJECT_ROOT"
docker build -t dbt-snowflake .

echo "2. Push sur ECR"
aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin $ECR_URL
docker tag dbt-snowflake:latest $ECR_URL:latest
docker push $ECR_URL:latest

echo "3. Déployer l'infrastructure"
cd "$SCRIPT_DIR"                          # ← ici les fichiers .tf
terraform init
terraform apply -auto-approve \
  -var="snowflake_private_key=$(cat $PROJECT_ROOT/rsa_key.p8)"

echo "✅ Déploiement terminé"
