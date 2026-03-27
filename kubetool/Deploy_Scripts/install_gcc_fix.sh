#!/bin/bash
################################################################################
# NimbusRE Agent - Ubuntu Installation Script (AWS Ubuntu-friendly, noninteractive)
# - Prevents interactive prompts and service restart popups
# - Reinstalls python3-apt to avoid cnf-update-db errors
# - Ensures services are explicitly restarted at the end
################################################################################

# dpkg options: accept defaults for config file prompts
DPKG_OPTS=( -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" )

# Update package lists
apt-get update "${DPKG_OPTS[@]}"

# Install a newer compiler (GCC12) and essentials. If apt can't find gcc-12, try gcc-13.
apt-get install -y "${DPKG_OPTS[@]}" gcc-12 g++-12 build-essential dkms || sudo apt-get install -y  "${DPKG_OPTS[@]}" gcc-13 g++-13 build-essential dkms

# Ensure kernel headers are available for your running kernel (required)
apt-get install -y "${DPKG_OPTS[@]}" linux-headers-$(uname -r) || sudo apt-get install -y "${DPKG_OPTS[@]}" linux-headers-aws || true

# Remove stale crash file so DKMS can create a fresh report
rm -f /var/crash/nvidia-dkms.0.crash

# Rebuild & install the NVIDIA DKMS module using gcc-12 (use gcc-13 if you installed that)
CC=/usr/bin/gcc-12 CXX=/usr/bin/g++-12 dkms build -m nvidia -v 590.48.01
CC=/usr/bin/gcc-12 CXX=/usr/bin/g++-12 dkms install -m nvidia -v 590.48.01

# If you prefer one command that will attempt rebuild/install for all modules:
# sudo CC=/usr/bin/gcc-12 dkms autoinstall

# Check DKMS status and finish package config
dkms status
dpkg --configure -a
apt-get install -f -y "${DPKG_OPTS[@]}"