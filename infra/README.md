# Terraform

Minimal AWS provisioning for the challenge:

- VPC with public/private subnets
- EKS cluster with managed node group
- PostgreSQL on Amazon RDS

## Usage

```bash
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
```

This stack assumes AWS credentials are already configured in the shell or CI runner.
