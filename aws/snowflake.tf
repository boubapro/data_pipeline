provider "snowflake" {
  organization_name = var.snowflake_organization_name
  account_name      = var.snowflake_account_name
  user              = var.snowflake_user
  role              = var.snowflake_role
  authenticator     = "JWT"
  private_key       = var.snowflake_private_key
}

# ─────────────────────────────────────────
# Warehouses
# ─────────────────────────────────────────
resource "snowflake_warehouse" "transform" {
  name           = "TRANSFORM_WH"
  warehouse_size = "XSMALL"
  auto_suspend   = 60
  auto_resume    = true
  comment        = "Warehouse dbt transformations"
}

resource "snowflake_warehouse" "monitor" {
  name           = "MONITOR_WH"
  warehouse_size = "XSMALL"
  auto_suspend   = 60
  auto_resume    = true
  comment        = "Warehouse monitoring"
}

# ─────────────────────────────────────────
# Rôles
# ─────────────────────────────────────────
resource "snowflake_account_role" "data_engineer" {
  name    = "DATA_ENGINEER"
  comment = "Accès complet aux transformations"
}

resource "snowflake_account_role" "data_analyst" {
  name    = "DATA_ANALYST"
  comment = "Lecture seule sur les marts"
}

# ─────────────────────────────────────────
# Grants TRANSFORM_WH
# ─────────────────────────────────────────
resource "snowflake_grant_privileges_to_account_role" "transform_wh_engineer" {
  account_role_name = snowflake_account_role.data_engineer.name
  privileges        = ["USAGE", "OPERATE"]

  on_account_object {
    object_type = "WAREHOUSE"
    object_name = snowflake_warehouse.transform.name
  }
}

resource "snowflake_grant_privileges_to_account_role" "transform_wh_analyst" {
  account_role_name = snowflake_account_role.data_analyst.name
  privileges        = ["USAGE"]

  on_account_object {
    object_type = "WAREHOUSE"
    object_name = snowflake_warehouse.transform.name
  }
}

# ─────────────────────────────────────────
# Grants MONITOR_WH
# ─────────────────────────────────────────
resource "snowflake_grant_privileges_to_account_role" "monitor_wh_engineer" {
  account_role_name = snowflake_account_role.data_engineer.name
  privileges        = ["USAGE", "OPERATE"]

  on_account_object {
    object_type = "WAREHOUSE"
    object_name = snowflake_warehouse.monitor.name
  }
}