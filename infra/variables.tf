variable "aws_region" {
  type        = string
  description = "AWS region for the infrastructure."
  default     = "us-east-1"
}

variable "project_name" {
  type        = string
  description = "Base name applied to AWS resources."
  default     = "service-order-api"
}

variable "cluster_name" {
  type        = string
  description = "EKS cluster name."
  default     = "service-order-eks"
}

variable "kubernetes_version" {
  type        = string
  description = "EKS Kubernetes version."
  default     = "1.31"
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR block for the VPC."
  default     = "10.40.0.0/16"
}

variable "node_instance_types" {
  type        = list(string)
  description = "EC2 instance types for the managed node group."
  default     = ["t3.medium"]
}

variable "node_desired_size" {
  type        = number
  description = "Desired number of worker nodes."
  default     = 2
}

variable "node_min_size" {
  type        = number
  description = "Minimum number of worker nodes."
  default     = 1
}

variable "node_max_size" {
  type        = number
  description = "Maximum number of worker nodes."
  default     = 4
}

variable "db_name" {
  type        = string
  description = "RDS PostgreSQL database name."
  default     = "service_order_db"
}

variable "db_username" {
  type        = string
  description = "RDS PostgreSQL username."
  default     = "service_order_user"
}

variable "db_password" {
  type        = string
  description = "RDS PostgreSQL password."
  sensitive   = true
}

variable "db_instance_class" {
  type        = string
  description = "RDS instance class."
  default     = "db.t4g.micro"
}

variable "db_allocated_storage" {
  type        = number
  description = "Allocated storage in GB for the RDS instance."
  default     = 20
}
