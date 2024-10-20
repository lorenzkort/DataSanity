provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "main" {
  name     = "DataSanityTest"
  location = "West Europe"
}

resource "azurerm_container_registry" "acr" {
  name                = "datasanityregistrytest"  # Ensure unique name
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Basic"
  admin_enabled       = true

  lifecycle {
    prevent_destroy = true  # Prevent accidental deletion during testing
  }
}

resource "azurerm_postgresql_server" "main" {
  name                = "datasanitypostgres"  # Ensure unique name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  administrator_login = "adminuser"
  administrator_login_password = "jfjjfjff"  # Ensure strong password in production
  sku_name            = "B_Gen5_1"  # Keep for test, consider lower tier for even cheaper
  storage_mb          = 512          # Reduced storage
  version             = "13"         # Use a newer version for long-term viability
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

resource "azurerm_virtual_network" "main" {
  name                = "app-vnet-test"  # Different name for test
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
}

resource "azurerm_subnet" "internal" {
  name                 = "internal"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_rabbitmq_cluster" "rabbitmq" {
  name                = "my-apptest-rabbitmq"  # Different name for test
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "Standard"  # Consider using the lowest SKU available

  lifecycle {
    prevent_destroy = true  # Prevent accidental deletion during testing
  }
}

resource "azurerm_kubernetes_cluster" "aks" {
  name                = "app-k8s-cluster-test"  # Different name for test
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  dns_prefix          = "datasanity-k8s-test"  # Different DNS prefix for test

  default_node_pool {
    name       = "default"
    node_count = 1  # Keep this minimal during testing
    vm_size    = "Standard_B2s"  # Smaller VM size for cost efficiency
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin    = "azure"
    service_cidr      = "10.0.0.0/16"
    dns_service_ip    = "10.0.0.10"
    docker_bridge_cidr = "172.17.0.1/16"
  }

  timeouts {
    create = "30m"  # Set a timeout for resource creation
    delete = "30m"  # Set a timeout for resource deletion
  }
}
