output "vpc_id" {
  value       = local.vpc_id
  description = "ID da VPC em uso."
}

output "public_subnet_id" {
  value       = local.public_subnet_id
  description = "Subnet publica em uso."
}

output "private_subnet_ids" {
  value       = local.private_subnet_ids
  description = "Subnets privadas em uso."
}

output "ec2_public_ip" {
  value       = var.allocate_eip ? aws_eip.app[0].public_ip : aws_instance.app.public_ip
  description = "IP publico da EC2."
}

output "ec2_public_dns" {
  value       = aws_instance.app.public_dns
  description = "DNS publico da EC2."
}

output "app_directory" {
  value       = var.app_directory
  description = "Diretorio esperado para a aplicacao na EC2."
}

output "rds_endpoint" {
  value       = aws_db_instance.postgres.endpoint
  description = "Endpoint do RDS PostgreSQL."
}

output "rds_database_name" {
  value       = aws_db_instance.postgres.db_name
  description = "Nome do banco PostgreSQL."
}

output "rds_username" {
  value       = aws_db_instance.postgres.username
  description = "Usuario do banco PostgreSQL."
  sensitive   = true
}
