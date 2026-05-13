"""
run_migrations.py
-----------------
Exécute uniquement les nouveaux fichiers SQL du dossier `migrations/`
qui n'ont pas encore été joués sur Snowflake.

Utilisation :
    python scripts/run_migrations.py

Variables d'environnement requises :
    SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PRIVATE_KEY_PATH,
    SNOWFLAKE_ROLE, SNOWFLAKE_WAREHOUSE, SNOWFLAKE_DATABASE
"""

import os
import sys
import hashlib
import logging
from pathlib import Path
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import snowflake.connector

# ─── Configuration ────────────────────────────────────────────────────────────

MIGRATIONS_DIR = Path(__file__).parent.parent / "migrations"
_db     = os.getenv("SNOWFLAKE_DATABASE", "SNOWFLAKE_LEARNING_DB")
_schema = os.getenv("SNOWFLAKE_SCHEMA", "PUBLIC")
TRACKING_TABLE = f"{_db}.{_schema}.MIGRATIONS_HISTORY"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def load_private_key():
    """Charge la clé privée RSA depuis le fichier."""
    key_path = os.environ["SNOWFLAKE_PRIVATE_KEY_PATH"]
    with open(key_path, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None,
            backend=default_backend(),
        )
    return private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )


def get_snowflake_connection():
    """Crée une connexion Snowflake via clé RSA."""
    required = [
        "SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_PRIVATE_KEY_PATH",
        "SNOWFLAKE_ROLE", "SNOWFLAKE_WAREHOUSE", "SNOWFLAKE_DATABASE", "SNOWFLAKE_SCHEMA",
    ]
    missing = [v for v in required if not os.getenv(v)]
    if missing:
        raise EnvironmentError(f"Variables manquantes : {', '.join(missing)}")

    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        private_key=load_private_key(),
        role=os.environ["SNOWFLAKE_ROLE"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema=os.environ["SNOWFLAKE_SCHEMA"],
    )


def file_checksum(path: Path) -> str:
    """Calcule le SHA-256 d'un fichier SQL."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def get_executed_migrations(cursor) -> set:
    """Retourne l'ensemble des noms de fichiers déjà exécutés."""
    cursor.execute(f"SELECT filename FROM {TRACKING_TABLE} WHERE status = 'SUCCESS'")
    return {row[0] for row in cursor.fetchall()}


def get_pending_migrations(executed: set) -> list[Path]:
    """
    Retourne les fichiers SQL du dossier migrations/ triés par nom
    qui n'ont pas encore été exécutés.
    Convention de nommage recommandée : V001__description.sql
    """
    if not MIGRATIONS_DIR.exists():
        raise FileNotFoundError(f"Dossier introuvable : {MIGRATIONS_DIR}")

    all_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    pending = [f for f in all_files if f.name not in executed]

    log.info(f"Fichiers trouvés : {len(all_files)} | Déjà exécutés : {len(executed)} | En attente : {len(pending)}")
    return pending


def split_sql_statements(sql: str) -> list[str]:
    """
    Découpe un fichier SQL en statements individuels.
    Gère les blocs $$ (procédures stockées Snowflake) sans les couper.
    """
    statements = []
    current    = []
    in_block   = False

    for line in sql.splitlines():
        stripped = line.strip()
        if stripped.count("$$") % 2 != 0:
            in_block = not in_block
        current.append(line)
        if not in_block and stripped.endswith(";"):
            stmt = "\n".join(current).strip()
            if stmt:
                statements.append(stmt)
            current = []

    leftover = "\n".join(current).strip()
    if leftover:
        statements.append(leftover)

    return statements


def run_sql_file(cursor, path: Path):
    """Exécute un fichier SQL (supporte les statements multiples et les blocs $$)."""
    sql        = path.read_text(encoding="utf-8")
    statements = split_sql_statements(sql)
    for stmt in statements:
        log.debug(f"  → {stmt[:80]}...")
        cursor.execute(stmt)


def mark_as_executed(cursor, filename: str, checksum: str, status: str = "SUCCESS"):
    """Enregistre la migration dans la table de tracking."""
    cursor.execute(
        f"""
        INSERT INTO {TRACKING_TABLE} (migration_id, filename, checksum, status)
        VALUES (%s, %s, %s, %s)
        """,
        (f"{filename}_{checksum[:8]}", filename, checksum, status),
    )


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    log.info("═══ Démarrage des migrations Snowflake ═══")

    conn = get_snowflake_connection()
    cursor = conn.cursor()

    try:
        executed = get_executed_migrations(cursor)
        pending = get_pending_migrations(executed)

        if not pending:
            log.info("✅ Aucune migration en attente. Rien à faire.")
            return

        errors = []

        for migration_file in pending:
            checksum = file_checksum(migration_file)
            log.info(f"▶  Exécution : {migration_file.name}")

            try:
                run_sql_file(cursor, migration_file)
                mark_as_executed(cursor, migration_file.name, checksum, "SUCCESS")
                conn.commit()
                log.info(f"✅ Succès : {migration_file.name}")

            except Exception as e:
                conn.rollback()
                mark_as_executed(cursor, migration_file.name, checksum, "FAILED")
                conn.commit()
                log.error(f"❌ Échec : {migration_file.name} → {e}")
                errors.append(migration_file.name)

        if errors:
            log.error(f"\n{len(errors)} migration(s) en échec : {errors}")
            sys.exit(1)

        log.info(f"\n✅ {len(pending)} migration(s) exécutée(s) avec succès.")

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
