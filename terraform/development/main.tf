locals {
  users_table_name = "${var.project_name}-users"
  visit_table_name = "${var.project_name}-visits"
  tags = {
    Project     = var.project_name
    Environment = "development"
  }
}

module "database" {
  source = "git::https://github.com/yuta15/47log-infra.git//terraform/modules/database?ref=main"

  tables = {
    (local.users_table_name) = {
      hash_key   = "user_id"
      attributes = { user_id = "S" }
    }
    (local.visit_table_name) = {
      hash_key  = "user_id"
      range_key = "visit_id"
      attributes = {
        user_id  = "S"
        visit_id = "S"
      }
    }
  }

  tags = local.tags
}

module "backend" {
  source = "git::https://github.com/yuta15/47log-infra.git//terraform/modules/backend?ref=main"

  project_name = var.project_name
  lambdas = {
    api = {
      route_path    = "$default"
      image_uri     = var.backend_initial_image_uri
      architecture  = var.backend_architecture
      authorization = "JWT"
      environment_variables = {
        USERS_TABLE_NAME = local.users_table_name
        VISIT_TABLE_NAME = local.visit_table_name
      }
      table_arns = module.database.table_arns
    }
  }

  jwt_authorizer = var.jwt_authorizer
  cors_configuration = length(var.cors_allow_origins) == 0 ? null : {
    allow_origins = var.cors_allow_origins
  }
  tags = local.tags
}
