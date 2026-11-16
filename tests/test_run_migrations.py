import tempfile
import unittest
from pathlib import Path
import os
import sys
from unittest.mock import patch

from scripts import run_migrations, write_dbt_profile


class MigrationRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.migrations_dir = Path(self.temp_dir.name)
        self.directory_patch = patch.object(
            run_migrations, "MIGRATIONS_DIR", self.migrations_dir
        )
        self.directory_patch.start()
        self.addCleanup(self.directory_patch.stop)
        self.addCleanup(self.temp_dir.cleanup)

    def test_only_versioned_files_are_pending_in_numeric_order(self):
        for name in (
            "V010__later.sql",
            "V002__earlier.sql",
            "drop_some_tables.sql",
            "notes.sql",
        ):
            (self.migrations_dir / name).write_text("SELECT 1;\n")

        pending = run_migrations.get_pending_migrations({})

        self.assertEqual(
            [path.name for path in pending],
            ["V002__earlier.sql", "V010__later.sql"],
        )

    def test_duplicate_versions_are_rejected(self):
        (self.migrations_dir / "V002__first.sql").write_text("SELECT 1;\n")
        (self.migrations_dir / "V002__second.sql").write_text("SELECT 2;\n")

        with self.assertRaisesRegex(ValueError, "dupliquée"):
            run_migrations.get_pending_migrations({})

    def test_modified_executed_migration_is_rejected(self):
        migration = self.migrations_dir / "V001__test.sql"
        migration.write_text("SELECT 1;\n")

        with self.assertRaisesRegex(ValueError, "modifiée"):
            run_migrations.get_pending_migrations(
                {migration.name: "not-the-file-checksum"}
            )

    def test_known_historic_migration_checksum_is_accepted(self):
        migration = self.migrations_dir / "V001__create_ref_table.sql"
        migration.write_text("SELECT 1;\n")
        previous_checksum = next(
            iter(run_migrations.HISTORIC_CHECKSUMS[migration.name])
        )

        self.assertEqual(
            run_migrations.get_pending_migrations(
                {migration.name: previous_checksum}
            ),
            [],
        )

    def test_out_of_order_migration_is_rejected(self):
        (self.migrations_dir / "V001__a.sql").write_text("SELECT 1;\n")
        (self.migrations_dir / "V003__c.sql").write_text("SELECT 1;\n")
        (self.migrations_dir / "V002__b.sql").write_text("SELECT 1;\n")
        executed = {
            "V001__a.sql": run_migrations.file_checksum(self.migrations_dir / "V001__a.sql"),
            "V003__c.sql": run_migrations.file_checksum(self.migrations_dir / "V003__c.sql"),
        }

        with self.assertRaisesRegex(ValueError, "hors ordre"):
            run_migrations.get_pending_migrations(executed)

    def test_destructive_pending_migration_is_rejected(self):
        for sql in (
            "DROP TABLE t;",
            "truncate table t;",
            "CREATE OR REPLACE TABLE t (id INT);",
            "CREATE OR REPLACE TRANSIENT TABLE t (id INT);",
        ):
            with self.subTest(sql=sql):
                (self.migrations_dir / "V004__x.sql").write_text(sql + "\n")
                with self.assertRaisesRegex(ValueError, "destructive"):
                    run_migrations.get_pending_migrations({})

    def test_destructive_migration_with_marker_is_accepted(self):
        (self.migrations_dir / "V004__x.sql").write_text(
            "-- migration:allow-destructive\nDROP TABLE old_table;\n"
        )
        pending = run_migrations.get_pending_migrations({})
        self.assertEqual([p.name for p in pending], ["V004__x.sql"])

    def test_destructive_keywords_in_comments_are_ignored(self):
        (self.migrations_dir / "V004__x.sql").write_text(
            "-- on ne fait pas de DROP TABLE ici\n"
            "/* TRUNCATE interdit */\nCREATE TABLE IF NOT EXISTS t (id INT);\n"
        )
        self.assertEqual(len(run_migrations.get_pending_migrations({})), 1)

    def test_legacy_migrations_are_exempt_from_destructive_check(self):
        (self.migrations_dir / "V003__legacy.sql").write_text("DROP TABLE t;\n")
        self.assertEqual(len(run_migrations.get_pending_migrations({})), 1)

    def test_tracking_table_requires_database_and_schema(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(EnvironmentError, "SNOWFLAKE_DATABASE"):
                run_migrations.tracking_table_name()

        with patch.dict(
            os.environ,
            {"SNOWFLAKE_DATABASE": "prod_db", "SNOWFLAKE_SCHEMA": "ops"},
            clear=True,
        ):
            self.assertEqual(
                run_migrations.tracking_table_name(),
                '"PROD_DB"."OPS".MIGRATIONS_HISTORY',
            )

    def test_sql_split_keeps_procedure_body_together(self):
        statements = run_migrations.split_sql_statements(
            "CREATE PROCEDURE p() AS $$\nBEGIN\nSELECT 1;\nEND;\n$$;\nSELECT 2;\n"
        )

        self.assertEqual(len(statements), 2)
        self.assertIn("SELECT 1;", statements[0])
        self.assertEqual(statements[1], "SELECT 2;")

    def test_profile_only_includes_a_set_passphrase(self):
        environment = {
            "SNOWFLAKE_ACCOUNT": "ci",
            "SNOWFLAKE_USER": "ci",
            "SNOWFLAKE_ROLE": "ci",
            "SNOWFLAKE_WAREHOUSE": "ci",
            "SNOWFLAKE_DATABASE": "CI_DATABASE",
            "SNOWFLAKE_SCHEMA": "CI_SCHEMA",
            "SNOWFLAKE_PRIVATE_KEY_PATH": "/tmp/unused-key",
        }
        with tempfile.TemporaryDirectory() as output_dir:
            with patch.dict(os.environ, environment, clear=True), patch.object(
                sys, "argv", ["write_dbt_profile.py", output_dir]
            ):
                write_dbt_profile.main()

            profile_path = Path(output_dir) / "profiles.yml"
            self.assertNotIn("private_key_passphrase", profile_path.read_text())
            self.assertEqual(profile_path.stat().st_mode & 0o777, 0o600)

            with patch.dict(
                os.environ,
                {**environment, "SNOWFLAKE_PRIVATE_KEY_PASSPHRASE": "test 'phrase"},
                clear=True,
            ), patch.object(sys, "argv", ["write_dbt_profile.py", output_dir]):
                write_dbt_profile.main()

            self.assertIn(
                "private_key_passphrase: \"test 'phrase\"",
                profile_path.read_text(),
            )


class RepositoryMigrationsTests(unittest.TestCase):
    """Contrôle les vraies migrations du dépôt, sans connexion Snowflake."""

    def test_repository_migrations_pass_pending_checks(self):
        pending = run_migrations.get_pending_migrations({})
        self.assertTrue(pending)

    def test_only_versioned_sql_files_live_in_migrations_dir(self):
        names = [p.name for p in run_migrations.MIGRATIONS_DIR.glob("*.sql")]
        unversioned = [n for n in names if not run_migrations.VERSIONED_MIGRATION.fullmatch(n)]
        self.assertEqual(unversioned, [])


if __name__ == "__main__":
    unittest.main()
