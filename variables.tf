variable "environment" {
  description = "Environment name (dev, prod, etc.)"
  type        = string
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "westeurope"
}

variable "claude_api_key" {
  description = "Claude API Key"
  type        = string
  sensitive   = true
}
