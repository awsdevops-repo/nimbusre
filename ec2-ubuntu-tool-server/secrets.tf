# --- SSH key: generate locally (Terraform), store private key in Secrets Manager ---
resource "tls_private_key" "ssh" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "rd" {
  key_name   = "${var.name}-key"
  public_key = tls_private_key.ssh.public_key_openssh

  tags = var.tags
}

resource "random_string" "pem_suffix" {
  length  = 4
  upper   = false
  lower   = true
  numeric = true
  special = false
}
resource "aws_secretsmanager_secret" "pem" {
  name        = "${var.name}/ssh-private-key-pem-${random_string.pem_suffix.result}"
  description = "EC2 SSH private key (PEM) for ${var.name}. Treat as sensitive."
  kms_key_id  = var.kms_key_id # optional; can be null
  tags        = var.tags
}

resource "aws_secretsmanager_secret_version" "pem_v" {
  secret_id     = aws_secretsmanager_secret.pem.id
  secret_string = tls_private_key.ssh.private_key_pem
}
