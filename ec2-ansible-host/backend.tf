terraform {
  backend "s3" {
    bucket = "s3-odie-dev-euwe1-tfstatefile"
    key    = "ec2-ansible-host/terraform.tfstate"
    region = "eu-west-1"
  }
}