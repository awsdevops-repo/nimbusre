# resource "aws_s3_object" "scripts_archive" {
#   bucket = local.scripts_bucket
#   key    = "${local.scripts_prefix}/${local.scripts_archive_name}"

#   source      = local.scripts_archive_path
#   source_hash = filesha256(local.scripts_archive_path)



#   tags = var.tags
# }

resource "null_resource" "fetch_and_extract_scripts" {
  triggers = {
    always_run = timestamp() # changes every plan/apply
  }
  depends_on = [
    aws_instance.tool_server
  ]

  connection {
    type        = "ssh"
    user        = "ubuntu"
    host        = aws_instance.tool_server.public_ip
    private_key = tls_private_key.ssh.private_key_pem
    timeout     = "5m"
  }

  provisioner "remote-exec" {
    inline = [
      "set -euo ",

      # Ensure awscli exists (Ubuntu)

      "sudo apt-get update -y && sudo apt-get install -y  unzip tar ",


      "curl https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip -o awscliv2.zip",
      "unzip -o awscliv2.zip ",
      "sudo ./aws/install --update",
      # Create destination
      "sudo mkdir -p ${var.unzip_target_dir}",
      "sudo mkdir -p tmp",
      "sudo chown -R ubuntu:ubuntu tmp",
      "sudo chown -R ubuntu:ubuntu ${var.unzip_target_dir}",

      # Download + extract
      "ARCHIVE=./tmp/${local.scripts_archive_name}",
      "aws s3 cp s3://${local.scripts_bucket}/${local.scripts_prefix}/${local.scripts_archive_name} $ARCHIVE",
      "tar -xzf $ARCHIVE -C ${var.unzip_target_dir}",

      # Optional: cleanup
      "rm -f $ARCHIVE",
      "cd ${var.unzip_target_dir}/kubetool && sudo bash install_gcc_fix.sh",
      "cd ${var.unzip_target_dir}/kubetool && sudo bash install_tools.sh",
      "cd ${var.unzip_target_dir}/kubetool && sudo bash deploy_app.sh"
    ]
  }

  #   # Re-run remote-exec if archive changes
  #   triggers = {
  #     s3_etag = aws_s3_object.scripts_archive.etag
  #   }
}
