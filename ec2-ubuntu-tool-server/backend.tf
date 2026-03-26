terraform {
  backend "s3" {
    bucket = "s3-odie-dev-euwe1-tfstatefile"
    key    = "ec2-ubuntu-tool-server/terraform.tfstate"
    region = "eu-west-1"
  }
}