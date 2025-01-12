#!/bin/bash
set -e

# Check if required tools are installed
command -v gh >/dev/null 2>&1 || { echo "GitHub CLI is required but not installed. Aborting." >&2; exit 1; }
command -v terraform >/dev/null 2>&1 || { echo "Terraform is required but not installed. Aborting." >&2; exit 1; }
command -v aws >/dev/null 2>&1 || { echo "AWS CLI is required but not installed. Aborting." >&2; exit 1; }

# Get AWS credentials
echo "Setting up AWS credentials..."
AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id)
AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key)

# Initialize and apply Terraform
echo "Initializing Terraform..."
cd infra/terraform
terraform init
terraform apply -auto-approve

# Get outputs from Terraform
ECR_REPOSITORY=$(terraform output -raw ecr_repository_url)
ECS_CLUSTER=$(terraform output -raw ecs_cluster_name)
ECS_SERVICE=$(terraform output -raw ecs_service_name)

# Set up GitHub secrets using gh CLI
echo "Setting up GitHub secrets..."
gh secret set AWS_ACCESS_KEY_ID --body "$AWS_ACCESS_KEY_ID"
gh secret set AWS_SECRET_ACCESS_KEY --body "$AWS_SECRET_ACCESS_KEY"
gh secret set ECR_REPOSITORY --body "$ECR_REPOSITORY"
gh secret set ECS_CLUSTER --body "$ECS_CLUSTER"
gh secret set ECS_SERVICE --body "$ECS_SERVICE"

echo "Setup complete!"