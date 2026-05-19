variable "aws_region" {
  type        = string
  description = "Regiao AWS."
  default     = "sa-east-1"
}

variable "project_name" {
  type        = string
  description = "Prefixo aplicado aos recursos."
  default     = "service-order-api"
}

variable "create_vpc" {
  type        = bool
  description = "Quando true, cria VPC e subnets. Quando false, reutiliza IDs existentes."
  default     = true
}

variable "existing_vpc_id" {
  type        = string
  description = "ID da VPC existente quando create_vpc=false."
  default     = ""
}

variable "existing_public_subnet_id" {
  type        = string
  description = "Subnet publica existente quando create_vpc=false."
  default     = ""
}

variable "existing_private_subnet_ids" {
  type        = list(string)
  description = "Subnets privadas existentes quando create_vpc=false."
  default     = []
}

variable "availability_zones" {
  type        = list(string)
  description = "Availability zones usadas quando create_vpc=true."
  default     = []
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR da VPC."
  default     = "10.40.0.0/16"
}

variable "public_subnet_cidr" {
  type        = string
  description = "CIDR da subnet publica."
  default     = "10.40.1.0/24"
}

variable "private_subnet_cidrs" {
  type        = list(string)
  description = "CIDRs das subnets privadas."
  default     = ["10.40.11.0/24", "10.40.12.0/24"]
}

variable "allowed_ssh_cidrs" {
  type        = list(string)
  description = "Origem permitida para SSH."
  default     = ["0.0.0.0/0"]
}

variable "app_ingress_cidrs" {
  type        = list(string)
  description = "Origem permitida para a API HTTP."
  default     = ["0.0.0.0/0"]
}

variable "ec2_instance_type" {
  type        = string
  description = "Tipo da instância EC2."
  default     = "t3.micro"
}

variable "ec2_key_name" {
  type        = string
  description = "Key pair da EC2."
  default     = ""
}

variable "ec2_ami_id" {
  type        = string
  description = "AMI customizada opcional."
  default     = ""
}

variable "allocate_eip" {
  type        = bool
  description = "Aloca Elastic IP para a EC2."
  default     = true
}

variable "app_directory" {
  type        = string
  description = "Diretorio da aplicação na EC2."
  default     = "/opt/service-order-api"
}

variable "docker_compose_version" {
  type        = string
  description = "Versao do Docker Compose plugin instalada no bootstrap."
  default     = "v2.27.0"
}

variable "db_name" {
  type        = string
  description = "Nome do banco PostgreSQL."
  default     = "service_order_db"
}

variable "db_username" {
  type        = string
  description = "Usuario do banco."
  default     = "service_order_user"
}

variable "db_password" {
  type        = string
  description = "Senha do banco."
  sensitive   = true
}

variable "db_instance_class" {
  type        = string
  description = "Classe do RDS."
  default     = "db.t4g.micro"
}

variable "db_allocated_storage" {
  type        = number
  description = "Armazenamento do RDS em GB."
  default     = 20
}

variable "db_engine_version" {
  type        = string
  description = "Versao do PostgreSQL."
  default     = "16.10"
}
