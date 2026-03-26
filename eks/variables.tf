variable "aws_region" {
  type    = string
  default = "eu-west-1"
}

variable "cluster_name" {
  type    = string
  default = "rd-eks-min-public"
}

variable "kubernetes_version" {
  type    = string
  default = "1.33"
}

variable "vpc_id" {
  type    = string
  default = "vpc-04f169a815c80c7fd"
}

variable "public_subnet_ids" {
  type = list(string)
  default = [
    "subnet-0548b16ca555e5897",
    "subnet-0931af6f2b0189d56"
  ]
}

# Fargate runs pods without EC2 nodes.
# Add namespaces you want to schedule onto Fargate.
variable "fargate_namespaces" {
  type        = list(string)
  description = "Namespaces to run on Fargate in addition to default"
  default     = ["default"] # add "rd-app1", "rd-app2" if you like
}

variable "tags" {
  type    = map(string)
  default = { Environment = "dev" }
}

# Role creation (full EKS IAM + kubectl via access entry)
variable "role_name" {
  type    = string
  default = "eks-full-kubectl"
}

variable "trusted_principal_arn" {
  type        = string
  description = "Who can assume this role (e.g., your GitHub Actions role, or an admin role/user ARN)"
  default     = "arn:aws:iam::658454555656:role/terraform-deploy"
}
