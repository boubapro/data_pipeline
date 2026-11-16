variable "snowflake_account" {
  description = "Snowflake account identifier"
  type        = string
  sensitive   = true
}

variable "snowflake_organization_name" {
  description = "Snowflake organization name"
  type        = string
}

variable "snowflake_account_name" {
  description = "Snowflake account name"
  type        = string
}

variable "snowflake_user" {
  description = "Snowflake username"
  type        = string
  sensitive   = true
}

variable "snowflake_database" {
  description = "Target Snowflake database"
  type        = string
  default     = "SNOWFLAKE_LEARNING_DB" # non sensible, ok en default
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
}

variable "snowflake_private_key" {
  description = "Private key used by the Terraform Snowflake provider"
  type        = string
  sensitive   = true
}

variable "snowflake_private_key_secret_arn" {
  description = "ARN of the Secrets Manager secret injected into the ECS task"
  type        = string
}

variable "snowflake_private_key_passphrase_secret_arn" {
  description = "Optional ARN of the key passphrase secret injected into the ECS task"
  type        = string
  default     = null
}

variable "aws_region" {
  description = "AWS region used for the ECR, ECS and CloudWatch resources"
  type        = string
  default     = "eu-west-1"
}

variable "subnet_ids" {
  description = "List of subnet IDs"
  type        = list(string)
}
