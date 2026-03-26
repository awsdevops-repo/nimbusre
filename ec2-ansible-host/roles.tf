resource "aws_iam_role" "tool_server" {
  name = "${var.name}-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect    = "Allow",
      Principal = { Service = "ec2.amazonaws.com" },
      Action    = "sts:AssumeRole"
    }]
  })
  tags = var.tags
}

resource "aws_iam_policy" "s3_get_kube_tools" {
  name = "${var.name}-s3-get-kube-tools"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect : "Allow",
      Action : ["s3:GetObject"],
      Resource : "arn:aws:s3:::s3-odie-dev-euwe1-tfstatefile/scripts/*"
      },
      { Effect : "Allow",
        Action : [
          "eks:DescribeCluster",
          "eks:ListClusters",
          "eks:ListUpdates",
          "eks:DescribeUpdate"
        ],
        Resource : "*"
      }
    ]
  })
  tags = var.tags
}


resource "aws_iam_role_policy_attachment" "attach_s3_read" {
  role       = aws_iam_role.tool_server.name
  policy_arn = aws_iam_policy.s3_get_kube_tools.arn
}

resource "aws_iam_instance_profile" "tool_server" {
  name = "${var.name}-instance-profile"
  role = aws_iam_role.tool_server.name
}
