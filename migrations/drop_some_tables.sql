-- drop_test_tables.sql
-- Supprime toutes les tables du schéma PUBLIC dont le nom contient "TEST"

CREATE OR REPLACE PROCEDURE SNOWFLAKE_LEARNING_DB.PUBLIC.DROP_TEST_TABLES()
RETURNS VARCHAR
LANGUAGE JAVASCRIPT
AS
$$
    var dropped = [];
    var errors  = [];

    // Récupère toutes les tables dont le nom contient TEST
    var query = `
        SELECT table_name
        FROM SNOWFLAKE_LEARNING_DB.information_schema.tables
        WHERE table_schema = 'PUBLIC'
          AND UPPER(table_name) LIKE '%TEST%'
          AND table_type = 'BASE TABLE'
        ORDER BY table_name
    `;

    var result = snowflake.execute({ sqlText: query });

    while (result.next()) {
        var tableName = result.getColumnValue(1);
        var dropSQL   = `DROP TABLE IF EXISTS SNOWFLAKE_LEARNING_DB.PUBLIC.${tableName}`;

        try {
            snowflake.execute({ sqlText: dropSQL });
            dropped.push(tableName);
        } catch (err) {
            errors.push(tableName + ': ' + err.message);
        }
    }

    if (dropped.length === 0 && errors.length === 0) {
        return "✅ Aucune table contenant 'TEST' trouvée.";
    }

    var msg = `✅ ${dropped.length} table(s) supprimée(s) : ${dropped.join(', ')}`;
    if (errors.length > 0) {
        msg += `\n❌ ${errors.length} erreur(s) : ${errors.join(', ')}`;
    }
    return msg;
$$;

-- Exécution
CALL SNOWFLAKE_LEARNING_DB.PUBLIC.DROP_TEST_TABLES();

-- Nettoyage de la procédure après usage (optionnel)
-- DROP PROCEDURE SNOWFLAKE_LEARNING_DB.PUBLIC.DROP_TEST_TABLES();
