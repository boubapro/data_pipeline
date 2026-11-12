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

Le fichier `profiles.yml` utilise les variables `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_ROLE`, `SNOWFLAKE_WAREHOUSE`, `SNOWFLAKE_DATABASE`, `SNOWFLAKE_SCHEMA` et `SNOWFLAKE_PRIVATE_KEY_PATH`. Pour une clé chiffrée, définissez aussi `SNOWFLAKE_PRIVATE_KEY_PASSPHRASE`. Placez-les dans `.env` (non versionné), protégez ce fichier avec `chmod 600 .env`, puis lancez `./run_dbt.sh`; le script restreint automatiquement les permissions de la clé. Le script utilise la cible `dev` par défaut; `DBT_TARGET` permet de choisir `dev`, `int` ou `prod`, et `DBT_TAG` est facultatif.
