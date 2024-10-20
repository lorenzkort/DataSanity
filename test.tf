provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "main" {
  name     = "DataSanityTest"  # Resource group for testing
  location = "West Europe"
}

resource "azurerm_postgresql_server" "main" {
  name                = "datasanitypostgres"  # Ensure unique name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  administrator_login = "adminuser"
  administrator_login_password = "jfjjfjff"  # Ensure a strong password
  sku_name            = "B_Gen5_1"  # Cost-effective SKU for testing
  storage_mb          = 512          # Minimal storage
  version             = "13"         # Use a stable version
  ssl_enforcement_enabled = true

  timeouts {
    create = "30m"  # Set a timeout for resource creation
    delete = "30m"  # Set a timeout for resource deletion
  }
}

resource "azurerm_postgresql_database" "datasanitydb" {
  name                = "userdb"
  resource_group_name = azurerm_resource_group.main.name
  server_name         = azurerm_postgresql_server.main.name
  charset             = "UTF8"
  collation           = "English_United States.1252"
}

output "db_url" {
  value = "postgresql://${azurerm_postgresql_server.main.administrator_login}:${azurerm_postgresql_server.main.administrator_login_password}@${azurerm_postgresql_server.main.fqdn}:5432/${azurerm_postgresql_database.datasanitydb.name}?sslmode=require"
}
