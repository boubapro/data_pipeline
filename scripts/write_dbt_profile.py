"""Write a dbt profile using only the connection settings in the environment."""

import json
import os
import sys
from pathlib import Path


REQUIRED_ENV_VARS = (
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_USER",
    "SNOWFLAKE_ROLE",
    "SNOWFLAKE_WAREHOUSE",
    "SNOWFLAKE_DATABASE",
    "SNOWFLAKE_SCHEMA",
    "SNOWFLAKE_PRIVATE_KEY_PATH",
)


def yaml_value(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    return json.dumps(value)


def main():
    missing = [name for name in REQUIRED_ENV_VARS if not os.getenv(name)]
    if missing:
        raise ValueError(f"Variables d'environnement manquantes : {', '.join(missing)}")

    output_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/dbt-profiles")
    output_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    output_dir.chmod(0o700)

    connection = {
        "type": "snowflake",
        "account": os.environ["SNOWFLAKE_ACCOUNT"],
        "user": os.environ["SNOWFLAKE_USER"],
        "private_key_path": os.environ["SNOWFLAKE_PRIVATE_KEY_PATH"],
        "role": os.environ["SNOWFLAKE_ROLE"],
        "warehouse": os.environ["SNOWFLAKE_WAREHOUSE"],
        "database": os.environ["SNOWFLAKE_DATABASE"],
        "schema": os.environ["SNOWFLAKE_SCHEMA"],
        "threads": 4,
        "transient": False,
    }
    passphrase = os.getenv("SNOWFLAKE_PRIVATE_KEY_PASSPHRASE")
    if passphrase:
        connection["private_key_passphrase"] = passphrase

    lines = ["data_pipeline:", "  target: dev", "  outputs:"]
    for target in ("dev", "int", "prod"):
        lines.append(f"    {target}:")
        for name, value in connection.items():
            lines.append(f"      {name}: {yaml_value(value)}")

    profile_path = output_dir / "profiles.yml"
    profile_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    profile_path.chmod(0o600)


if __name__ == "__main__":
    main()
