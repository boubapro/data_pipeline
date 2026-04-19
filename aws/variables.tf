variable "snowflake_account"     { default = "ysscfpp-gn61729" }
variable "snowflake_user"        { default = "BOUBACARB" }
variable "snowflake_database"    { default = "SNOWFLAKE_LEARNING_DB" }
variable "snowflake_schema"      { default = "PUBLIC" }
variable "snowflake_warehouse"   { default = "COMPUTE_WH" }
variable "snowflake_role"        { default = "ACCOUNTADMIN" }
variable "snowflake_private_key" { sensitive = true }
variable "subnet_ids"            { type = list(string) }
