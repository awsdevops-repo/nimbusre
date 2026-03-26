terraform {
  backend "s3" {
    bucket = "s3-odie-dev-euwe1-tfstatefile"
    key    = "eks-minimal-demo/terraform.tfstate"
    region = "eu-west-1"
  }
}