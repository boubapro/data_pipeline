variable "snowflake_account" {
  description = "Snowflake account identifier"
  type        = string
  sensitive   = true
}

variable "snowflake_user" {
  description = "Snowflake username"
  type        = string
  sensitive   = true
}

variable "snowflake_database" {
  description = "Target Snowflake database"
  type        = string
  default     = "SNOWFLAKE_LEARNING_DB"   # non sensible, ok en default
}

variable "snowflake_schema" {
  description = "Target Snowflake schema"
  type        = string
  default     = "PUBLIC"
}

variable "snowflake_warehouse" {
  description = "Snowflake virtual warehouse"
  type        = string
  default     = "COMPUTE_WH"
}

variable "snowflake_role" {
  description = "Snowflake role"
  type        = string
  default     = "ACCOUNTADMIN"
}

variable "snowflake_private_key" {
  description = "Snowflake private key for authentication"
  type        = string
  sensitive   = true
}

variable "subnet_ids" {
  description = "List of subnet IDs"
  type        = list(string)
}
