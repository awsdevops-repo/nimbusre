# EIP for NAT
resource "aws_eip" "nat" {
  domain = "vpc"
  tags   = var.tags
}

# Put NAT in any public subnet you already have
resource "aws_nat_gateway" "this" {
  allocation_id = aws_eip.nat.id
  subnet_id     = var.public_subnet_ids[0]
  tags          = var.tags
}

# Send private subnet egress to NAT
resource "aws_route" "private_default" {
  route_table_id         = aws_route_table.private.id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.this.id
}
