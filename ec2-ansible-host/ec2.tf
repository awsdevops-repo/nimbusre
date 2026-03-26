# # --- EC2 instance ---
resource "aws_instance" "tool_server" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = "t3.medium"
  subnet_id                   = var.subnet_id
  vpc_security_group_ids      = [aws_security_group.tool_server.id]
  key_name                    = aws_key_pair.rd.key_name
  associate_public_ip_address = var.associate_public_ip
  iam_instance_profile        = aws_iam_instance_profile.tool_server.name

  root_block_device {
    volume_size           = var.root_volume_gb
    volume_type           = "gp3"
    delete_on_termination = true
  }


  tags = merge(var.tags, { Name = var.name })
}

