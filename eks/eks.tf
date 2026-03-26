module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 21.0"

  name               = var.cluster_name
  kubernetes_version = var.kubernetes_version

  vpc_id     = var.vpc_id
  subnet_ids = var.public_subnet_ids

  # Public-only cluster access
  endpoint_public_access  = true
  endpoint_private_access = false

  # Enable EKS Cluster Access Management (Access Entries)
  authentication_mode = "API_AND_CONFIG_MAP"

  # Makes the identity running Terraform cluster-admin on creation (handy bootstrap)
  enable_cluster_creator_admin_permissions = true



  # -----------------------------
  # Fargate (NO managed node groups)
  # -----------------------------
  eks_managed_node_groups = {}





  depends_on = [aws_subnet.private_a, aws_subnet.private_b]
  tags       = var.tags
}

# remove fargate_profiles from module.eks

resource "aws_eks_fargate_profile" "kube_system_coredns" {
  cluster_name           = module.eks.cluster_name
  fargate_profile_name   = "${var.cluster_name}-kube-system"
  pod_execution_role_arn = aws_iam_role.fargate_pod_exec.arn
  subnet_ids             = [aws_subnet.private_a.id, aws_subnet.private_b.id]

  selector {
    namespace = "kube-system"
    # omit labels so CoreDNS will match
  }

  depends_on = [module.eks] # wait for cluster & module outputs to be stable
}

resource "aws_eks_fargate_profile" "default" {
  cluster_name           = module.eks.cluster_name
  fargate_profile_name   = "${var.cluster_name}-default"
  pod_execution_role_arn = aws_iam_role.fargate_pod_exec.arn
  subnet_ids             = [aws_subnet.private_a.id, aws_subnet.private_b.id]

  selector {
    namespace = "default"
  }

  depends_on = [module.eks]
}
