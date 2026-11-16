-- macros/safe_bi_swap.sql

{#
  Retourne le schéma BI associé à un schéma FEED.
  Exemple : VENTES_FEED -> VENTES
#}
{% macro get_main_schema(feed_schema) %}
  {% set schema_upper = feed_schema | upper %}

  {% if schema_upper.endswith('_FEED') %}
    {{ return(feed_schema[:-5]) }}
  {% else %}
    {{ return(feed_schema) }}
  {% endif %}
{% endmacro %}


{#
  Publie une table FEED dans le schéma BI.

  - Si la table FEED n'existe pas : aucune action.
  - Si la table BI existe : SWAP.
  - Sinon : CLONE.
#}
{% macro swap_table(tbl, feed_schema) %}

  {% set main_schema = get_main_schema(feed_schema) %}
  {% set database = target.database %}

  {% set feed_table = database ~ '.' ~ feed_schema ~ '.' ~ tbl %}
  {% set bi_schema = database ~ '.' ~ main_schema %}
  {% set bi_table = bi_schema ~ '.' ~ tbl %}

  {# Créer le schéma BI si nécessaire #}
  {% do run_query(
    'CREATE SCHEMA IF NOT EXISTS ' ~ bi_schema
  ) %}

  {# Vérifier que la table FEED existe bien #}
  {% set feed_query %}
    SELECT COUNT(*)
    FROM {{ database }}.INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = '{{ feed_schema | upper }}'
      AND TABLE_NAME = '{{ tbl | upper }}'
      AND TABLE_TYPE = 'BASE TABLE'
  {% endset %}

  {% set feed_result = run_query(feed_query) %}
  {% set feed_exists =
    feed_result.columns[0].values()[0] > 0
  %}

  {% if not feed_exists %}

    {% do log(
      'SKIP : table FEED absente : ' ~ feed_table,
      info=true
    ) %}

  {% else %}

    {# Vérifier l'existence de la table BI #}
    {% set bi_query %}
      SELECT COUNT(*)
      FROM {{ database }}.INFORMATION_SCHEMA.TABLES
      WHERE TABLE_SCHEMA = '{{ main_schema | upper }}'
        AND TABLE_NAME = '{{ tbl | upper }}'
        AND TABLE_TYPE = 'BASE TABLE'
    {% endset %}

    {% set bi_result = run_query(bi_query) %}
    {% set bi_exists =
      bi_result.columns[0].values()[0] > 0
    %}

    {% if bi_exists %}

      {% do run_query(
        'ALTER TABLE ' ~ bi_table ~
        ' SWAP WITH ' ~ feed_table
      ) %}

      {% do log(
        'SWAP OK : ' ~ bi_table ~
        ' <-> ' ~ feed_table,
        info=true
      ) %}

    {% else %}

      {% do run_query(
        'CREATE TABLE ' ~ bi_table ~
        ' CLONE ' ~ feed_table
      ) %}

      {% do log(
        'CLONE OK : ' ~ feed_table ~
        ' -> ' ~ bi_table,
        info=true
      ) %}

    {% endif %}

  {% endif %}

{% endmacro %}


{#
  Point d'entrée de publication.

  Le périmètre est déterminé à partir des résultats dbt,
  et non à partir de toutes les tables présentes dans FEED.

  À appeler dans un contexte où "results" est disponible,
  par exemple on-run-end.
#}
{% macro safe_bi_swap() %}

  {% if execute and flags.WHICH in ['run', 'build'] %}

    {% set select_arg =
      invocation_args_dict.get('select')
      or invocation_args_dict.get('models')
    %}

    {% set is_full_run =
      (select_arg is none)
      or ((select_arg or []) | length == 0)
    %}

    {% if is_full_run %}
      {% do log(
        'Publication complète : modèles datamart réussis',
        info=true
      ) %}
    {% else %}
      {% do log(
        'Publication ciblée : modèles datamart réussis',
        info=true
      ) %}
    {% endif %}

    {% set published = [] %}

    {% for res in results %}

      {% if res.node.resource_type == 'model'
            and res.status == 'success'
            and 'datamart' in res.node.tags %}

        {% set tbl = res.node.alias or res.node.name %}
        {% set feed_schema = res.node.schema %}
        {% set table_key =
          (feed_schema | upper) ~ '.' ~ (tbl | upper)
        %}

        {# Éviter de traiter deux fois la même table #}
        {% if table_key not in published %}

          {% do published.append(table_key) %}

          {% do log(
            'Publication du modèle : ' ~ table_key,
            info=true
          ) %}

          {% do swap_table(tbl, feed_schema) %}

        {% endif %}

      {% elif res.node.resource_type == 'model'
              and res.status == 'success' %}

        {% do log(
          'SKIP : modèle hors datamart : ' ~ res.node.name,
          info=true
        ) %}

      {% endif %}

    {% endfor %}

    {% do log(
      'Publication terminée : ' ~ (published | length) ~
      ' table(s) traitée(s).',
      info=true
    ) %}

  {% endif %}

{% endmacro %}