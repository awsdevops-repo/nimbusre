variable "aws_region" {
  type    = string
  default = "eu-west-1"
}

variable "name" {
  type    = string
  default = "ubuntu-ansible-host"
}

variable "vpc_id" {
  type    = string
  default = "vpc-04f169a815c80c7fd"
}
variable "local_zip_path" {
  type    = string
  default = "./tools/kube_tools.tar"
}

variable "unzip_target_dir" {
  type    = string
  default = "/home/ubuntu/kubetool1"
}

variable "subnet_id" {
  type    = string
  default = "subnet-0548b16ca555e5897"
}


variable "associate_public_ip" {
  type    = bool
  default = true
}

variable "root_volume_gb" {
  type    = number
  default = 20
}

variable "ssh_allowed_cidrs" {
  type    = list(string)
  default = ["0.0.0.0/0"] # 🔒 change to your VPN/office CIDR
}

variable "open_vnc" {
  type    = bool
  default = false
}

variable "vnc_allowed_cidrs" {
  type    = list(string)
  default = ["0.0.0.0/0"] # only used if open_vnc=true; restrict heavily
}

variable "rdp_allowed_cidrs" {
  type    = list(string)
  default = ["0.0.0.0/0"] # 🔒 change to your VPN/office CIDR
}


variable "vnc_password" {
  type      = string
  sensitive = true
  default   = "Passwd@123" # 🔒 change me
}

variable "kms_key_id" {
  type        = string
  default     = null
  description = "Optional KMS key ARN/ID for Secrets Manager encryption"
}

variable "tags" {
  type    = map(string)
  default = {}
}




variable "ubuntu_version" {
  description = "Ubuntu LTS version to use: 22.04 or 20.04"
  type        = string
  default     = "22.04"
  validation {
    condition     = contains(["22.04", "20.04"], var.ubuntu_version)
    error_message = "ubuntu_version must be '22.04' or '20.04'."
  }
}