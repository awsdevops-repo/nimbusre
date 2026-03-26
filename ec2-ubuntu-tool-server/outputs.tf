output "instance_id" { value = aws_instance.tool_server }
output "public_ip" { value = aws_instance.tool_server.public_ip }
output "private_ip" { value = aws_instance.tool_server.private_ip }
output "ami_used" {
  description = "AMI ID selected"
  value       = data.aws_ami.ubuntu.id
}

# output "key_pair_name" { value = aws_key_pair.rd.key_name }

# output "pem_secret_arn" { value = aws_secretsmanager_secret.pem.arn }