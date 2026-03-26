resource "aws_iam_role" "fargate_pod_exec" {
  name = "${var.cluster_name}-fargate-pod-exec"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect    = "Allow",
      Principal = { Service = "eks-fargate-pods.amazonaws.com" },
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "fargate_exec_policy" {
  role       = aws_iam_role.fargate_pod_exec.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSFargatePodExecutionRolePolicy"
}

resource "aws_iam_role_policy_attachment" "ecr_readonly" {
  role       = aws_iam_role.fargate_pod_exec.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

# Wire it into EVERY fargate profile:
# (add this attribute inside both profiles)
# pod_execution_role_arn = aws_iam_role.fargate_pod_exec.arn
