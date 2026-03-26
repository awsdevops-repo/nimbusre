locals {
  ami_name_filter      = var.ubuntu_version == "22.04" ? "ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" : "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"
  scripts_bucket       = "s3-odie-dev-euwe1-tfstatefile"
  scripts_prefix       = "scripts"
  scripts_archive_name = "kube_tools.tar"
  scripts_archive_path = "${path.module}/tools/${local.scripts_archive_name}"
}
