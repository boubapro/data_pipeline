provider "aws" {
  region = "eu-west-1"           # ← changer selon ta région
}

# ─────────────────────────────────────────
# ECR — registry Docker
# ─────────────────────────────────────────
resource "aws_ecr_repository" "dbt" {
  name = "dbt-snowflake"
}

# ─────────────────────────────────────────
# ECS Cluster
# ─────────────────────────────────────────
resource "aws_ecs_cluster" "dbt" {
  name = "dbt-cluster"
}

# ─────────────────────────────────────────
# IAM Role pour ECS Task
# ─────────────────────────────────────────
resource "aws_iam_role" "ecs_task" {
  name = "dbt-ecs-task-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task" {
  role       = aws_iam_role.ecs_task.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# ─────────────────────────────────────────
# ECS Task Definition
# ─────────────────────────────────────────
resource "aws_ecs_task_definition" "dbt" {
  family                   = "dbt-task"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name  = "dbt"
    image = "${aws_ecr_repository.dbt.repository_url}:latest"
    environment = [
      { name = "DBT_TAG",             value = "monday_19h" },        # ← corrigé
      { name = "SNOWFLAKE_ACCOUNT",   value = var.snowflake_account },
      { name = "SNOWFLAKE_USER",      value = var.snowflake_user },
      { name = "SNOWFLAKE_DATABASE",  value = var.snowflake_database },
      { name = "SNOWFLAKE_SCHEMA",    value = var.snowflake_schema },
      { name = "SNOWFLAKE_WAREHOUSE", value = var.snowflake_warehouse },
      { name = "SNOWFLAKE_ROLE",      value = var.snowflake_role },
      { name = "SNOWFLAKE_PRIVATE_KEY", value = var.snowflake_private_key }
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = "/ecs/dbt"
        awslogs-region        = "eu-west-1"
        awslogs-stream-prefix = "dbt"
      }
    }
  }])
}

# ─────────────────────────────────────────
# CloudWatch Logs
# ─────────────────────────────────────────
resource "aws_cloudwatch_log_group" "dbt" {
  name              = "/ecs/dbt"
  retention_in_days = 30
}

# ─────────────────────────────────────────
# IAM Role pour EventBridge Scheduler
# ─────────────────────────────────────────
resource "aws_iam_role" "scheduler" {
  name = "dbt-scheduler-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "scheduler.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy" "scheduler" {
  role = aws_iam_role.scheduler.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["ecs:RunTask", "iam:PassRole"]
      Resource = "*"
    }]
  })
}

# ─────────────────────────────────────────
# EventBridge Scheduler — tous les lundis à 19h Paris
# ─────────────────────────────────────────
resource "aws_scheduler_schedule" "dbt" {
  name       = "dbt-monday-19h"                          # ← corrigé
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression          = "cron(0 19 ? * MON *)"  # ← corrigé
  schedule_expression_timezone = "Europe/Paris"

  target {
    arn      = aws_ecs_cluster.dbt.arn
    role_arn = aws_iam_role.scheduler.arn

    ecs_parameters {
      task_definition_arn = aws_ecs_task_definition.dbt.arn
      launch_type         = "FARGATE"

      network_configuration {
        subnets          = var.subnet_ids
        assign_public_ip = true
      }
    }
  }
}
