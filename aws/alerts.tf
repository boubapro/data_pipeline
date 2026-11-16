# ─────────────────────────────────────────
# Alerte : échec de la tâche dbt planifiée
# ─────────────────────────────────────────
resource "aws_sns_topic" "dbt_alerts" {
  name = "dbt-task-failures"
}

resource "aws_sns_topic_subscription" "dbt_alerts_email" {
  count     = var.alert_email == "" ? 0 : 1
  topic_arn = aws_sns_topic.dbt_alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

resource "aws_cloudwatch_event_rule" "dbt_task_failed" {
  name        = "dbt-task-failed"
  description = "Tâche ECS dbt arrêtée en erreur ou impossible à démarrer"

  event_pattern = jsonencode({
    source        = ["aws.ecs"]
    "detail-type" = ["ECS Task State Change"]
    detail = {
      clusterArn = [aws_ecs_cluster.dbt.arn]
      lastStatus = ["STOPPED"]
    }
    "$or" = [
      { detail = { containers = { exitCode = [{ "anything-but" = 0 }] } } },
      { detail = { stopCode = ["TaskFailedToStart"] } }
    ]
  })
}

resource "aws_cloudwatch_event_target" "dbt_task_failed" {
  rule = aws_cloudwatch_event_rule.dbt_task_failed.name
  arn  = aws_sns_topic.dbt_alerts.arn
}

resource "aws_sns_topic_policy" "dbt_alerts" {
  arn = aws_sns_topic.dbt_alerts.arn
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "events.amazonaws.com" }
      Action    = "sns:Publish"
      Resource  = aws_sns_topic.dbt_alerts.arn
    }]
  })
}
