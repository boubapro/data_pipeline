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


if __name__ == "__main__":
    unittest.main()
