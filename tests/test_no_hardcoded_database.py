import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent
FORBIDDEN = "SNOWFLAKE_LEARNING_DB"
SCANNED = [
    "models", "macros", "scripts", "aws", "migrations", ".github", "profiles.yml",
    "dbt_project.yml", ".gitlab-ci.yml", "run_dbt.sh", "Dockerfile", "Makefile",
]
SUFFIXES = {".sql", ".yml", ".yaml", ".py", ".tf", ".sh", ""}


class NoHardcodedDatabaseTests(unittest.TestCase):
    def test_learning_database_is_not_hardcoded(self):
        offenders = []
        for entry in SCANNED:
            base = ROOT / entry
            files = [base] if base.is_file() else base.rglob("*")
            for path in files:
                if (
                    path.is_file()
                    and path.suffix in SUFFIXES
                    and "install" != path.name
                    and "__pycache__" not in path.parts
                    and ".terraform" not in path.parts
                ):
                    if FORBIDDEN in path.read_text(encoding="utf-8", errors="ignore"):
                        offenders.append(str(path.relative_to(ROOT)))
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
