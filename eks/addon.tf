resource "aws_eks_addon" "coredns" {
  cluster_name = module.eks.cluster_name
  addon_name   = "coredns"
  # Fargate: run CoreDNS on Fargate
  configuration_values        = jsonencode({ computeType = "Fargate" })
  resolve_conflicts_on_create = "OVERWRITE"
  resolve_conflicts_on_update = "OVERWRITE"

  depends_on = [aws_eks_fargate_profile.kube_system_coredns]
}

resource "aws_eks_addon" "vpc_cni" {
  cluster_name                = module.eks.cluster_name
  addon_name                  = "vpc-cni"
  resolve_conflicts_on_create = "OVERWRITE"
  resolve_conflicts_on_update = "OVERWRITE"
}

resource "aws_eks_addon" "kube_proxy" {
  cluster_name                = module.eks.cluster_name
  addon_name                  = "kube-proxy"
  resolve_conflicts_on_create = "OVERWRITE"
  resolve_conflicts_on_update = "OVERWRITE"
}
