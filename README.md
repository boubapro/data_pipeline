# data_pipeline

## Environnements GitLab

Le pipeline GitLab cible les branches `dev`, `int` et `main` :

- `dev` utilise l’environnement GitLab `dev` et la cible dbt `dev`.
- `int` utilise l’environnement GitLab `int` et la cible dbt `int`.
- `main` utilise l’environnement GitLab `production` et la cible dbt `prod`. Le job de production est manuel.

Dans **Settings > CI/CD > Variables**, créez pour chacune des portées `dev`, `int` et `production` les variables `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_ROLE`, `SNOWFLAKE_WAREHOUSE`, `SNOWFLAKE_DATABASE` et `SNOWFLAKE_SCHEMA`. Ajoutez `SNOWFLAKE_PRIVATE_KEY` comme variable de type **File**. Si la clé est chiffrée, ajoutez `SNOWFLAKE_PRIVATE_KEY_PASSPHRASE` comme variable standard. Pour toutes les variables, choisissez la portée d’environnement exacte (`dev`, `int` ou `production`); marquez les secrets comme **Protected** lorsque la branche correspondante est protégée. Utilisez des identifiants Snowflake distincts pour chaque environnement.

Le job vérifie que les variables requises sont définies et que le fichier de clé existe avant de lancer dbt. La phrase de passe est facultative.

Dans **Settings > CI/CD > Protected environments**, protégez `production` et limitez les déployeurs autorisés. Protégez également la branche `main` et les variables des secrets de production. La configuration du dépôt rend le job manuel bloquant, mais les autorisations de déploiement doivent être définies dans GitLab.

### Connexion dbt locale

Le profil dbt utilise les variables `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_ROLE`, `SNOWFLAKE_WAREHOUSE`, `SNOWFLAKE_DATABASE`, `SNOWFLAKE_SCHEMA` et `SNOWFLAKE_PRIVATE_KEY_PATH`. Pour une clé chiffrée, définissez aussi `SNOWFLAKE_PRIVATE_KEY_PASSPHRASE`. Placez-les dans `.env` (non versionné), protégez ce fichier avec `chmod 600 .env`, puis lancez `./run_dbt.sh`; le script génère un profil temporaire protégé et restreint les permissions de la clé. Le script utilise la cible `dev` par défaut; `DBT_TARGET` permet de choisir `dev`, `int` ou `prod`, et `DBT_TAG` est facultatif.

### Source housing

La table `loyer` n'est plus recherchée dans une base codée en dur. Elle est lue dans la base de la target dbt (schéma `PUBLIC`) sauf si `HOUSING_SOURCE_DATABASE` et/ou `HOUSING_SOURCE_SCHEMA` sont définies (variables GitHub/GitLab, `.env` en local, variables Terraform `housing_source_database` / `housing_source_schema` pour ECS). Si la table se trouve toujours dans l'ancienne base d'apprentissage, définissez `HOUSING_SOURCE_DATABASE` avec son nom pour chaque environnement. Les variables Terraform `snowflake_database` et `snowflake_schema` n'ont plus de valeur par défaut, et `scripts/run_migrations.py` exige `SNOWFLAKE_DATABASE` et `SNOWFLAKE_SCHEMA`.

### Isolation des environnements

La macro `generate_schema_name` isole les environnements par le code : en `prod`, les schémas gardent leur nom (ex. `DATAMART_SALES_FEED`) ; en `dev` et `int`, ils sont préfixés par la cible (ex. `DEV_DATAMART_SALES_FEED`, publié vers `DEV_DATAMART_SALES`). Un run non-prod ne peut donc pas écraser les tables de production, même sur la même base Snowflake. La tâche ECS planifiée définit `DBT_TARGET` via la variable Terraform `dbt_target` (défaut `prod`) ; `run_dbt.sh` utilise `dev` par défaut.

### Qualité, incrémental et alertes

- Les modèles incrémentaux recalculent une fenêtre de recul (`incremental_lookback_months`, défaut 1 mois ; `incremental_lookback_days`, défaut 1 jour) pour absorber les données tardives, et acceptent les nouvelles colonnes (`append_new_columns`). Exemple : `dbt build --vars '{incremental_lookback_months: 3}'`.
- Les tests `not_null` / `relationships` ajoutés sur `f_sales` sont en `severity: warn` : ils signalent sans bloquer la publication BI. Passez-les en `error` une fois les données source assainies.
- Terraform crée un topic SNS et une règle EventBridge qui notifient (variable `alert_email`) l'échec de la tâche ECS planifiée, y compris un échec de démarrage.
- L'image Docker tourne en utilisateur non-root et lance `/project/run_dbt.sh`.

### Publication BI

Les pipelines utilisent `dbt build` (modèles + tests). La macro `safe_bi_swap` s'exécute en `on-run-end` et ne publie les tables du datamart vers le schéma BI que si **aucun** modèle ni test n'est en échec ou ignoré ; sinon la publication est annulée et les tables BI restent inchangées. Elle ne s'exécute plus après un simple `dbt run`.

### Migrations Snowflake

Le runner `scripts/run_migrations.py` exécute uniquement les fichiers versionnés `V001__description.sql`, dans l'ordre numérique ; les autres fichiers SQL du dossier sont ignorés. Règles appliquées :

- Les migrations exécutées sont suivies par checksum : modifier une migration déjà appliquée bloque le déploiement (V001 et V002 conservent une exception limitée à leur checksum historique connu). V001 à V003 sont donc immuables, même si elles se recoupent.
- Une migration en attente plus ancienne que la dernière version exécutée est refusée : créez toujours une nouvelle version.
- À partir de V004, toute instruction destructive (`DROP`, `TRUNCATE`, `CREATE OR REPLACE TABLE/SCHEMA/DATABASE`) est refusée, sauf marqueur explicite `-- migration:allow-destructive` ajouté après revue. Ce contrôle est aussi exécuté par les tests de la CI.
- Le DDL Snowflake est validé automatiquement : une migration qui échoue en cours de route n'est pas annulée. Écrivez des migrations idempotentes (`CREATE ... IF NOT EXISTS`, `MERGE`) ; l'instruction en échec est indiquée dans l'erreur et la migration est marquée `FAILED` avant relance.
- Les scripts ponctuels (ex. nettoyage de tables de test) ne doivent pas être versionnés dans `migrations/`.

La base et le schéma de l'historique (`MIGRATIONS_HISTORY`) sont ceux de la cible Snowflake configurée.

### Déploiement AWS ECS

Avant `aws/deploy.sh`, stockez la clé privée PEM destinée à l'exécution dbt dans AWS Secrets Manager et définissez `SNOWFLAKE_PRIVATE_KEY_SECRET_ARN` avec son ARN, `AWS_REGION` si nécessaire, et les paramètres Terraform Snowflake/AWS requis. Pour une clé chiffrée, définissez aussi `SNOWFLAKE_PRIVATE_KEY_PASSPHRASE_SECRET_ARN`. Le rôle d'exécution ECS ne peut lire que ces secrets. Le rôle GitHub `production` doit être configuré comme environnement protégé pour les workflows manuels de production; AWS EventBridge est l'unique ordonnanceur hebdomadaire.
