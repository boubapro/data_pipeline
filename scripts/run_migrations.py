"""
Exécute les nouvelles migrations Snowflake versionnées du dossier migrations/.

Convention : V001__description.sql, V002__description.sql, etc.
Les scripts SQL sans version ne sont jamais exécutés automatiquement.

Garde-fous :
- une migration en attente dont la version est inférieure à la dernière
  version déjà exécutée est refusée (ordre strict) ;
- à partir de V004, une migration contenant une instruction destructive
  (DROP, TRUNCATE, CREATE OR REPLACE TABLE/SCHEMA/DATABASE) est refusée
  sauf si elle porte explicitement le marqueur `-- migration:allow-destructive` ;
- le DDL Snowflake est validé automatiquement (auto-commit) : une migration
  qui échoue en cours de route n'est PAS annulée. Écrire des migrations
  idempotentes (CREATE ... IF NOT EXISTS, MERGE) pour pouvoir les rejouer.
"""

import hashlib
import logging
import os
import re
from pathlib import Path

import snowflake.connector
from cryptography.hazmat.primitives import serialization

MIGRATIONS_DIR = Path(__file__).parent.parent / "migrations"
VERSIONED_MIGRATION = re.compile(r"^V([0-9]+)__[a-zA-Z0-9_]+\.sql$")
ALLOW_DESTRUCTIVE_MARKER = "-- migration:allow-destructive"
# V001 à V003 sont déjà appliquées et immuables : le contrôle ne couvre que la suite.
DESTRUCTIVE_CHECK_FROM_VERSION = 4
DESTRUCTIVE_PATTERNS = (
    re.compile(r"\bDROP\s+\w+", re.IGNORECASE),
    re.compile(r"\bTRUNCATE\b", re.IGNORECASE),
    re.compile(
        r"\bCREATE\s+OR\s+REPLACE\s+(?:TRANSIENT\s+|TEMPORARY\s+)?"
        r"(?:TABLE|SCHEMA|DATABASE)\b",
        re.IGNORECASE,
    ),
)
HISTORIC_CHECKSUMS = {
    "V001__create_ref_table.sql": {
        "2350c639fddfb8ffa264d142f13c8bd40507a52eed01d155d1c7307a03eb69e2"
    },
    "V002__create_ref_country.sql": {
        "dc58c4fb36976c348d2ef618aedc83f72a69bb1db2e40c87143afcbb21e34cc5"
    },
}


def quote_identifier(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_$]*", value):
        raise ValueError(f"Identifiant Snowflake invalide : {value!r}")
    return f'"{value.upper()}"'


def tracking_table_name() -> str:
    """Table de suivi, dans la base et le schéma de la cible configurée.

    Aucune valeur par défaut : une base absente doit échouer plutôt que de
    migrer silencieusement un environnement qui n'est pas celui attendu.
    """
    missing = [
        name
        for name in ("SNOWFLAKE_DATABASE", "SNOWFLAKE_SCHEMA")
        if not os.getenv(name)
    ]
    if missing:
        raise EnvironmentError(f"Variables manquantes : {', '.join(missing)}")
    database = quote_identifier(os.environ["SNOWFLAKE_DATABASE"])
    schema = quote_identifier(os.environ["SNOWFLAKE_SCHEMA"])
    return f"{database}.{schema}.MIGRATIONS_HISTORY"


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


def load_private_key():
    """Charge une clé privée RSA depuis un fichier."""
    key_path = os.environ["SNOWFLAKE_PRIVATE_KEY_PATH"]
    passphrase = os.getenv("SNOWFLAKE_PRIVATE_KEY_PASSPHRASE", "").encode() or None
    with open(key_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=passphrase,
        )
    return private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )


def get_snowflake_connection():
    """Crée une connexion Snowflake par authentification RSA."""
    required = [
        "SNOWFLAKE_ACCOUNT",
        "SNOWFLAKE_USER",
        "SNOWFLAKE_PRIVATE_KEY_PATH",
        "SNOWFLAKE_ROLE",
        "SNOWFLAKE_WAREHOUSE",
        "SNOWFLAKE_DATABASE",
        "SNOWFLAKE_SCHEMA",
    ]
    missing = [name for name in required if not os.getenv(name)]
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
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ensure_tracking_table(cursor):
    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {tracking_table_name()} (
            migration_id VARCHAR NOT NULL,
            filename VARCHAR NOT NULL,
            checksum VARCHAR NOT NULL,
            status VARCHAR NOT NULL
        )
        """
    )


def get_executed_migrations(cursor) -> dict[str, str]:
    cursor.execute(
        f"SELECT filename, checksum FROM {tracking_table_name()} WHERE status = 'SUCCESS'"
    )
    return {row[0]: row[1] for row in cursor.fetchall()}


def strip_sql_comments(sql: str) -> str:
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.DOTALL)
    return re.sub(r"--[^\n]*", " ", sql)


def find_destructive_statements(sql: str) -> list[str]:
    """Retourne les instructions destructives d'un script, hors commentaires."""
    if ALLOW_DESTRUCTIVE_MARKER in sql:
        return []
    code = strip_sql_comments(sql)
    return sorted(
        {match.group(0).upper() for pattern in DESTRUCTIVE_PATTERNS
         for match in pattern.finditer(code)}
    )


def migration_version(filename: str):
    match = VERSIONED_MIGRATION.fullmatch(filename)
    return int(match.group(1)) if match else None


def get_pending_migrations(executed: dict[str, str]) -> list[Path]:
    """Sélectionne les migrations versionnées et refuse les versions ambiguës."""
    if not MIGRATIONS_DIR.exists():
        raise FileNotFoundError(f"Dossier introuvable : {MIGRATIONS_DIR}")

    versioned = []
    seen_versions = set()
    for path in MIGRATIONS_DIR.glob("*.sql"):
        match = VERSIONED_MIGRATION.fullmatch(path.name)
        if not match:
            log.warning("Fichier SQL ignoré (nom non versionné) : %s", path.name)
            continue
        version = int(match.group(1))
        if version in seen_versions:
            raise ValueError(f"Version de migration dupliquée : {version}")
        seen_versions.add(version)
        versioned.append((version, path))

    versioned.sort(key=lambda item: item[0])
    for _, path in versioned:
        if path.name in executed and executed[path.name] != file_checksum(path):
            if executed[path.name] not in HISTORIC_CHECKSUMS.get(path.name, set()):
                raise ValueError(
                    f"La migration déjà exécutée a été modifiée : {path.name}"
                )
            log.warning(
                "Migration historique reconnue par son checksum : %s", path.name
            )

    pending = [path for _, path in versioned if path.name not in executed]

    executed_versions = [
        v for v in (migration_version(name) for name in executed) if v is not None
    ]
    if executed_versions and pending:
        highest = max(executed_versions)
        for path in pending:
            if migration_version(path.name) < highest:
                raise ValueError(
                    f"Migration hors ordre : {path.name} est antérieure à la "
                    f"version déjà exécutée V{highest:03d}. Créez une nouvelle "
                    "version au lieu d'insérer une migration dans le passé."
                )

    for path in pending:
        if migration_version(path.name) < DESTRUCTIVE_CHECK_FROM_VERSION:
            continue
        destructive = find_destructive_statements(path.read_text(encoding="utf-8"))
        if destructive:
            raise ValueError(
                f"Instruction destructive dans {path.name} : "
                f"{', '.join(destructive)}. Ajoutez le marqueur "
                f"'{ALLOW_DESTRUCTIVE_MARKER}' après revue si c'est voulu."
            )
    log.info(
        "Migrations versionnées : %d | Déjà exécutées : %d | En attente : %d",
        len(versioned),
        len(executed),
        len(pending),
    )
    return pending


def split_sql_statements(sql: str) -> list[str]:
    """Découpe le SQL en statements, en conservant les blocs $$...$$."""
    statements = []
    current = []
    in_block = False

    for line in sql.splitlines():
        stripped = line.strip()
        if stripped.count("$$") % 2:
            in_block = not in_block
        current.append(line)
        if not in_block and stripped.endswith(";"):
            statement = "\n".join(current).strip()
            if statement:
                statements.append(statement)
            current = []

    leftover = "\n".join(current).strip()
    if leftover:
        statements.append(leftover)

    return [
        statement
        for statement in statements
        if any(
            line.strip() and not line.strip().startswith("--")
            for line in statement.splitlines()
        )
    ]


def run_sql_file(cursor, path: Path):
    statements = split_sql_statements(path.read_text(encoding="utf-8"))
    for index, statement in enumerate(statements, start=1):
        log.debug("Exécution SQL : %s...", statement[:80])
        try:
            cursor.execute(statement)
        except Exception as error:
            raise RuntimeError(
                f"{path.name} : échec de l'instruction {index}/{len(statements)} "
                f"({statement[:80]!r}...)"
            ) from error


def mark_as_executed(cursor, filename: str, checksum: str, status: str):
    cursor.execute(
        f"""
        MERGE INTO {tracking_table_name()} AS target
        USING (
            SELECT %s AS migration_id, %s AS filename, %s AS checksum, %s AS status
        ) AS source
        ON target.filename = source.filename
        WHEN MATCHED THEN UPDATE SET
            migration_id = source.migration_id,
            checksum = source.checksum,
            status = source.status
        WHEN NOT MATCHED THEN INSERT (migration_id, filename, checksum, status)
        VALUES (source.migration_id, source.filename, source.checksum, source.status)
        """,
        (f"{filename}_{checksum[:8]}", filename, checksum, status),
    )


def main():
    log.info("═══ Démarrage des migrations Snowflake ═══")
    conn = get_snowflake_connection()
    cursor = conn.cursor()

    try:
        ensure_tracking_table(cursor)
        conn.commit()
        executed = get_executed_migrations(cursor)
        pending = get_pending_migrations(executed)

        for migration_file in pending:
            checksum = file_checksum(migration_file)
            log.info("Exécution : %s", migration_file.name)
            try:
                run_sql_file(cursor, migration_file)
                mark_as_executed(cursor, migration_file.name, checksum, "SUCCESS")
                conn.commit()
                log.info("Migration réussie : %s", migration_file.name)
            except Exception as error:
                # Le DDL Snowflake est auto-commit : rien n'est annulé ici.
                log.error(
                    "Échec de %s : les instructions déjà exécutées restent "
                    "appliquées. Corrigez puis relancez (migration idempotente).",
                    migration_file.name,
                )
                try:
                    mark_as_executed(cursor, migration_file.name, checksum, "FAILED")
                    conn.commit()
                except Exception:
                    log.exception("Impossible d'enregistrer le statut FAILED")
                raise RuntimeError(
                    f"Échec de la migration {migration_file.name}"
                ) from error

        log.info("%d migration(s) exécutée(s) avec succès.", len(pending))
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
