resource "aws_eks_access_entry" "admin_role" {
  cluster_name  = var.cluster_name
  principal_arn = aws_iam_role.tool_server.arn
  type          = "STANDARD"
}

resource "aws_eks_access_policy_association" "admin_role_cluster_admin" {
  cluster_name  = var.cluster_name
  principal_arn = aws_iam_role.tool_server.arn

  policy_arn = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"

  access_scope {
    type = "cluster"
  }

}

resource "aws_eks_access_policy_association" "admin_role_eks_admin" {
  cluster_name  = var.cluster_name
  principal_arn = aws_iam_role.tool_server.arn

  policy_arn = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSAdminPolicy"

  access_scope {
    type = "cluster"
  }

}
