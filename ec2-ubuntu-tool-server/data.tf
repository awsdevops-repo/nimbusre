data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = [local.ami_name_filter]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  filter {
    name   = "architecture"
    values = ["x86_64"]
  }

  filter {
    name   = "root-device-type"
    values = ["ebs"]
  }
}

# Pull from S3 and extract to /opt/kube_tools at boot
data "cloudinit_config" "tool_server_kube_tools" {
  gzip          = true
  base64_encode = true

  part {
    filename     = "10-fetch-kube-tools.sh"
    content_type = "text/x-shellscript"
    content      = <<-BASH
      #!/bin/bash
      set -euxo pipefail
      export DEBIAN_FRONTEND=noninteractive

      # Minimal deps
      apt-get update
      apt-get install -y awscli tar

      # Fetch tar from S3
      mkdir -p /opt/kube_tools
      aws s3 cp s3://s3-odie-dev-euwe1-tfstatefile/kube_tools.tar /opt/kube_tools/kube_tools.tar

      # Sanity check (should be >> 4KB)
      test $(stat -c '%s' /opt/kube_tools/kube_tools.tar) -gt 1000000

      # Extract
      tar -xf /opt/kube_tools/kube_tools.tar -C /opt/kube_tools

      # Ownership for ubuntu (ignore if user doesn't exist)
      chown -R ubuntu:ubuntu /opt/kube_tools || true

      # Optional: list contents
      ls -la /opt/kube_tools || true
    BASH
  }
}
