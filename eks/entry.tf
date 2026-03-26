resource "aws_eks_access_entry" "admin_role" {
  cluster_name  = var.cluster_name
  principal_arn = "arn:aws:iam::658454555656:role/admin"
  type          = "STANDARD"
  depends_on    = [module.eks]
}

resource "aws_eks_access_policy_association" "admin_role_cluster_admin" {
  cluster_name  = var.cluster_name
  principal_arn = "arn:aws:iam::658454555656:role/admin"

  policy_arn = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"

  access_scope {
    type = "cluster"
  }

  depends_on = [aws_eks_access_entry.admin_role]
}
resource "aws_iam_role" "eks_full_kubectl" {
  name = var.role_name

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        AWS = var.trusted_principal_arn
      }
      Action = "sts:AssumeRole"
    }]
  })

  tags = var.tags
}

# Full EKS IAM permissions (very broad)
resource "aws_iam_policy" "eks_full" {
  name = "${var.role_name}-eks-full"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "EKSFullAccess"
        Effect = "Allow"
        Action = [
          "eks:*"
        ]
        Resource = "*"
      },
      # Needed in practice for kubectl auth flows/tools to call STS
      {
        Sid    = "STSCallerIdentity"
        Effect = "Allow"
        Action = [
          "sts:GetCallerIdentity"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_eks_full" {
  role       = aws_iam_role.eks_full_kubectl.name
  policy_arn = aws_iam_policy.eks_full.arn
}

# -------------------------------
# EKS Access Entry (authn)
# -------------------------------
resource "aws_eks_access_entry" "this" {
  cluster_name  = var.cluster_name
  principal_arn = aws_iam_role.eks_full_kubectl.arn
  type          = "STANDARD"
  depends_on    = [module.eks]
}

# -------------------------------
# EKS Access Policy (authz for kubectl)
# Cluster admin => can run any kubectl command
# -------------------------------
resource "aws_eks_access_policy_association" "cluster_admin" {
  cluster_name  = var.cluster_name
  principal_arn = aws_iam_role.eks_full_kubectl.arn
  policy_arn    = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"

  access_scope {
    type = "cluster"
  }

  depends_on = [aws_eks_access_entry.this]
}