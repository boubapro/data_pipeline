# data_pipeline

## Environnements GitLab

Le pipeline GitLab cible les branches `dev`, `int` et `main` :

- `dev` utilise l’environnement GitLab `dev` et la cible dbt `dev`.
- `int` utilise l’environnement GitLab `int` et la cible dbt `int`.
- `main` utilise l’environnement GitLab `production` et la cible dbt `prod`. Le job de production est manuel.

Dans **Settings > CI/CD > Variables**, créez pour chacun de ces environnements les variables `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_ROLE`, `SNOWFLAKE_WAREHOUSE`, `SNOWFLAKE_DATABASE` et `SNOWFLAKE_SCHEMA`, avec la portée d’environnement correspondante (`dev`, `int` ou `production`). Ajoutez aussi `SNOWFLAKE_PRIVATE_KEY` comme variable de type **File**, avec la même portée. Utilisez des identifiants Snowflake distincts pour chaque environnement.

Dans **Settings > CI/CD > Protected environments**, protégez `production` et limitez les déployeurs autorisés. Protégez également la branche `main` et les variables des secrets de production. La configuration du dépôt rend le job manuel bloquant, mais les autorisations de déploiement doivent être définies dans GitLab.
