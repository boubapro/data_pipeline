{#
  Nom de schéma par environnement.

  - prod : schéma personnalisé tel quel (ex. DATAMART_SALES_FEED) -> les
    noms consommés par la BI ne changent pas.
  - dev / int : schéma préfixé par la target (ex. DEV_DATAMART_SALES_FEED),
    pour qu'un run hors production ne puisse jamais écraser les tables de
    production, même si SNOWFLAKE_DATABASE est identique.

  Sans schéma personnalisé, on garde target.schema (déjà propre à chaque
  environnement via SNOWFLAKE_SCHEMA).
#}
{% macro generate_schema_name(custom_schema_name, node) -%}
  {%- if custom_schema_name is none -%}
    {{ target.schema }}
  {%- elif target.name == 'prod' -%}
    {{ custom_schema_name | upper | trim }}
  {%- else -%}
    {{ (target.name ~ '_' ~ (custom_schema_name | trim)) | upper }}
  {%- endif -%}
{%- endmacro %}
