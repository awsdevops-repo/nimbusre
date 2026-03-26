# # Get the VPC CIDR for SG ingress
# data "aws_vpc" "this" {
#   id = var.vpc_id
# }

# # SG for interface VPC endpoints (HTTPS)
# resource "aws_security_group" "vpce_https" {
#   name        = "${var.cluster_name}-vpce-https"
#   description = "Allow HTTPS from VPC to VPC Endpoints"
#   vpc_id      = var.vpc_id

#   ingress {
#     description = "HTTPS from VPC"
#     from_port   = 443
#     to_port     = 443
#     protocol    = "tcp"
#     cidr_blocks = [data.aws_vpc.this.cidr_block]
#   }

#   egress {
#     description      = "All egress"
#     from_port        = 0
#     to_port          = 0
#     protocol         = "-1"
#     cidr_blocks      = ["0.0.0.0/0"]
#     ipv6_cidr_blocks = ["::/0"]
#   }

#   tags = var.tags
# }
