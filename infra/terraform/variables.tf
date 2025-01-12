variable "aws_region" {
  description = "AWS region"
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name"
  default     = "my-app"
}

variable "ecr_repository_name" {
  description = "Name of ECR repository"
  default     = "my-app-repo"
}

variable "cluster_name" {
  description = "Name of ECS cluster"
  default     = "my-app-cluster"
}

variable "service_name" {
  description = "Name of ECS service"
  default     = "my-app-service"
}

variable "container_name" {
  description = "Name of container"
  default     = "my-app-container"
}

variable "subnet_ids" {
  description = "Subnet IDs for ECS service"
  type        = list(string)
}