data "aws_availability_zones" "available" {}

locals {
  # pick the first two AZs in the region
  az_a = data.aws_availability_zones.available.names[0]
  az_b = data.aws_availability_zones.available.names[1]
}

resource "aws_subnet" "private_a" {
  vpc_id                  = var.vpc_id
  cidr_block              = "172.31.48.0/20"
  availability_zone       = local.az_a
  map_public_ip_on_launch = false

  tags = merge(var.tags, {
    Name                                        = "${var.cluster_name}-private-a"
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
    "kubernetes.io/role/internal-elb"           = "1"
  })
}

resource "aws_subnet" "private_b" {
  vpc_id                  = var.vpc_id
  cidr_block              = "172.31.64.0/20"
  availability_zone       = local.az_b
  map_public_ip_on_launch = false

  tags = merge(var.tags, {
    Name                                        = "${var.cluster_name}-private-b"
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
    "kubernetes.io/role/internal-elb"           = "1"
  })
}

# Private route table (no IGW route => private)
resource "aws_route_table" "private" {
  vpc_id = var.vpc_id

  tags = merge(var.tags, {
    Name = "${var.cluster_name}-private-rt"
  })
}

resource "aws_route_table_association" "private_a" {
  subnet_id      = aws_subnet.private_a.id
  route_table_id = aws_route_table.private.id
}

resource "aws_route_table_association" "private_b" {
  subnet_id      = aws_subnet.private_b.id
  route_table_id = aws_route_table.private.id
}

output "private_subnet_ids" {
  value = [aws_subnet.private_a.id, aws_subnet.private_b.id]
}
