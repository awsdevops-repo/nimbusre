# --- Security Group ---
resource "aws_security_group" "tool_server" {
  name        = "${var.name}-sg"
  description = "R&D Ubuntu tool server"
  vpc_id      = var.vpc_id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.ssh_allowed_cidrs
  }
  
  ingress {
    description = "MimbusSRE"
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = var.rdp_allowed_cidrs
  }
   ingress {
    description = "MimbusSRE"
    from_port   = 3001
    to_port     = 3001
    protocol    = "tcp"
    cidr_blocks = var.rdp_allowed_cidrs
  }
  ingress {
    description = "MimbusSRE"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = var.rdp_allowed_cidrs
  }

  ingress {
    description = "RDP"
    from_port   = 3389
    to_port     = 3389
    protocol    = "tcp"
    cidr_blocks = var.rdp_allowed_cidrs
  }
  egress {
    description = "All outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = var.tags
}
