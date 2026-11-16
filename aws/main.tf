provider "aws" {
  region = var.aws_region
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

resource "aws_iam_role_policy" "ecs_secret" {
  name = "dbt-snowflake-private-key"
  role = aws_iam_role.ecs_task.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = ["secretsmanager:GetSecretValue"]
      Resource = concat(
        [var.snowflake_private_key_secret_arn],
        var.snowflake_private_key_passphrase_secret_arn == null
        ? []
        : [var.snowflake_private_key_passphrase_secret_arn]
      )
    }]
  })
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
      { name = "SNOWFLAKE_ACCOUNT", value = var.snowflake_account },
      { name = "SNOWFLAKE_USER", value = var.snowflake_user },
      { name = "SNOWFLAKE_DATABASE", value = var.snowflake_database },
      { name = "SNOWFLAKE_SCHEMA", value = var.snowflake_schema },
      { name = "SNOWFLAKE_WAREHOUSE", value = var.snowflake_warehouse },
      { name = "SNOWFLAKE_ROLE", value = var.snowflake_role },
      { name = "DBT_TARGET", value = var.dbt_target },
      { name = "HOUSING_SOURCE_DATABASE", value = var.housing_source_database },
      { name = "HOUSING_SOURCE_SCHEMA", value = var.housing_source_schema },
      { name = "DBT_TAG", value = "every_monday_19h" }
    ]
    secrets = concat(
      [{
        name      = "SNOWFLAKE_PRIVATE_KEY"
        valueFrom = var.snowflake_private_key_secret_arn
      }],
      var.snowflake_private_key_passphrase_secret_arn == null ? [] : [{
        name      = "SNOWFLAKE_PRIVATE_KEY_PASSPHRASE"
        valueFrom = var.snowflake_private_key_passphrase_secret_arn
      }]
    )
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = "/ecs/dbt"
        awslogs-region        = var.aws_region
        awslogs-stream-prefix = "dbt"
      }
    }
  }])

  depends_on = [
    aws_cloudwatch_log_group.dbt,
    aws_iam_role_policy.ecs_secret
  ]
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
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["ecs:RunTask"]
        Resource = aws_ecs_task_definition.dbt.arn
      },
      {
        Effect   = "Allow"
        Action   = ["iam:PassRole"]
        Resource = aws_iam_role.ecs_task.arn
        Condition = {
          StringEquals = {
            "iam:PassedToService" = "ecs-tasks.amazonaws.com"
          }
        }
      }
    ]
  })
}

# ─────────────────────────────────────────
# EventBridge Scheduler — tous les lundis à 19h Paris
# ─────────────────────────────────────────
resource "aws_scheduler_schedule" "dbt" {
  name       = "dbt-monday-19h" # ← corrigé
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression          = "cron(0 19 ? * MON *)" # ← corrigé
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

# ─────────────────────────────────────────
# ECR Lifecycle Policy — keep 3 latest images
# ─────────────────────────────────────────
resource "aws_ecr_lifecycle_policy" "dbt" {
  repository = aws_ecr_repository.dbt.name
  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Garder seulement les 3 dernières images"
      selection = {
        tagStatus   = "any"
        countType   = "imageCountMoreThan"
        countNumber = 3
      }
      action = { type = "expire" }
    }]
  })
}
