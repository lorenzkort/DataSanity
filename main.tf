terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.0"
    }
  }
}
provider "azurerm" {
  features {}
}

provider "null" {
  # No configuration needed for null provider
}

data "azurerm_client_config" "current" {}

resource "azurerm_resource_group" "main" {
  name     = "rg-sql-lineage-${var.environment}"
  location = var.location
}

resource "azurerm_service_plan" "main" {
  name                = "asp-sql-lineage-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  os_type            = "Linux"
  sku_name           = "B1"
}

resource "azurerm_key_vault" "main" {
  name                = "kv-sql-lineage-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tenant_id          = data.azurerm_client_config.current.tenant_id
  sku_name           = "standard"

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id

    secret_permissions = [
      "Get",
      "List",
      "Set",
      "Delete"
    ]
  }
}

resource "azurerm_key_vault_secret" "claude_api_key" {
  name         = "claude-api-key"
  value        = var.claude_api_key
  key_vault_id = azurerm_key_vault.main.id
}

resource "azurerm_container_registry" "main" {
  name                = "acrsqllineage${var.environment}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Basic"
  admin_enabled       = true
}

# Create the web app first
resource "azurerm_linux_web_app" "main" {
  name                = "app-sql-lineage-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  service_plan_id     = azurerm_service_plan.main.id

  site_config {
    application_stack {
      docker_image_name   = "${azurerm_container_registry.main.login_server}/sql-lineage:latest"
      docker_registry_url = "https://${azurerm_container_registry.main.login_server}"
    }
  }

  app_settings = {
    "WEBSITES_PORT"                  = "8000"
    "SCM_DO_BUILD_DURING_DEPLOYMENT" = "true"
  }

  identity {
    type = "SystemAssigned"
  }
}

# Create access policy for web app
resource "azurerm_key_vault_access_policy" "webapp" {
  key_vault_id = azurerm_key_vault.main.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = azurerm_linux_web_app.main.identity[0].principal_id

  secret_permissions = [
    "Get",
    "List"
  ]

  depends_on = [
    azurerm_linux_web_app.main
  ]
}

# Update the web app settings after access policy is created
resource "null_resource" "update_app_settings" {
  triggers = {
    app_settings = "${azurerm_key_vault_secret.claude_api_key.version}"
  }

  provisioner "local-exec" {
    command = <<EOT
      az webapp config appsettings set \
        --name ${azurerm_linux_web_app.main.name} \
        --resource-group ${azurerm_resource_group.main.name} \
        --settings ANTHROPIC_API_KEY="@Microsoft.KeyVault(SecretUri=${azurerm_key_vault_secret.claude_api_key.versionless_id})"
    EOT
  }

  depends_on = [
    azurerm_key_vault_access_policy.webapp
  ]
}
