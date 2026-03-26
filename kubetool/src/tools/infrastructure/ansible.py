import os
import tempfile
import subprocess
from typing import Literal, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool


# Keep this tight. Expand only as needed.
ALLOWED_COMMANDS = {
    "software_list",       # List installed packages (Linux: apt/yum/dnf, Windows: wmic)
    "software_version",    # Get specific software version
    "os_info",            # Get OS and version info
    "service_status",     # Check service status
}

DENY_FLAGS = {"--vault-password-file", "-k", "--ask-pass"}  # Don't allow interactive/vault prompts

class AnsibleInput(BaseModel):
    command: Literal["software_list", "software_version", "os_info", "service_status"] = Field(
        ..., description="Allowed: software_list/software_version/os_info/service_status"
    )
    hosts: str = Field(..., description="Target host pattern (e.g. 'all', 'linux_servers', 'windows_servers', 'hostname')")
    software_name: Optional[str] = Field(None, description="Package name to query (required for software_version)")
    inventory_file: Optional[str] = Field(None, description="Path to Ansible inventory file")
    extra_vars: Optional[dict] = Field(default_factory=dict, description="Extra variables for playbook")


@tool("ansible_inventory", args_schema=AnsibleInput)
def ansible_tool(
    command: str,
    hosts: str,
    software_name: Optional[str] = None,
    inventory_file: Optional[str] = None,
    extra_vars: Optional[dict] = None,
):
    """
    Run Ansible commands to query software inventory across Linux and Windows hosts.
    Supports listing installed packages, checking versions, and OS info.
    """

    if extra_vars is None:
        extra_vars = {}

    # Validate command
    if command not in ALLOWED_COMMANDS:
        return f"Command not allowed: {command}"

    # Check for denied flags in inventory_file path
    if inventory_file and any(flag in inventory_file for flag in DENY_FLAGS):
        return "Not allowed to use vault or interactive password flags."

    # Use default inventory if not provided
    if not inventory_file:
        inventory_file = os.path.expanduser("~/.ansible/hosts")

    # Validate inventory file exists
    if not os.path.exists(inventory_file):
        return f"Inventory file not found: {inventory_file}"

    # Build playbook content based on command
    playbook_content = _build_playbook(command, hosts, software_name, extra_vars)

    if not playbook_content:
        return f"Invalid command or missing required parameters for {command}"

    # Execute playbook via tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(playbook_content)
        playbook_path = f.name

    try:
        cmd = [
            "ansible-playbook",
            playbook_path,
            "-i", inventory_file,
            "-v",  # Verbose output
        ]

        out = subprocess.check_output(
            cmd,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=120,  # 2 minute timeout for inventory queries
        )
        return out

    except subprocess.CalledProcessError as e:
        return f"Ansible playbook failed:\n{e.output}"
    except FileNotFoundError:
        return "ansible-playbook not found. Please install Ansible."
    except Exception as e:
        return f"Error running inventory query: {str(e)}"
    finally:
        try:
            os.remove(playbook_path)
        except OSError:
            pass


def _build_playbook(command: str, hosts: str, software_name: Optional[str], extra_vars: dict) -> str:
    """Build Ansible playbook YAML for the given command."""

    if command == "software_list":
        return f"""---
- hosts: {hosts}
  gather_facts: yes
  tasks:
    - name: List installed packages on Linux
      block:
        - name: List packages (apt)
          shell: |
            dpkg -l | grep '^ii' | awk '{{print $2, $3}}'
          register: apt_list
          when: ansible_os_family == 'Debian'

        - name: List packages (dnf)
          shell: |
            dnf list installed | grep -v '@' | awk '{{print $1}}'
          register: dnf_list
          when: ansible_os_family == 'RedHat' and ansible_distribution_major_version is version('8', '>=')

        - name: List packages (yum)
          shell: |
            yum list installed | awk '{{print $1}}'
          register: yum_list
          when: ansible_os_family == 'RedHat' and ansible_distribution_major_version is version('8', '<')

        - name: Show results
          debug:
            msg: "Installed packages: {{ apt_list.stdout | default(dnf_list.stdout | default(yum_list.stdout)) }}"
      when: ansible_os_family != 'Windows'

    - name: List installed software on Windows
      block:
        - name: Query installed software via WMI
          win_powershell:
            script: |
              Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* |
              Select-Object DisplayName, DisplayVersion | 
              Format-Table -AutoSize
          register: win_software

        - name: Show results
          debug:
            msg: "{{ win_software.output }}"
      when: ansible_os_family == 'Windows'
"""

    elif command == "software_version":
        if not software_name:
            return None  # Missing required parameter

        return f"""---
- hosts: {hosts}
  gather_facts: yes
  tasks:
    - name: Get software version - {{{{ software_name }}}}
      block:
        - name: Check package on Linux
          shell: |
            dpkg -l | grep {software_name} || rpm -qa | grep {software_name} || dnf list {software_name} || echo "Not found"
          register: pkg_version
          changed_when: false

        - name: Show version
          debug:
            msg: "{{ pkg_version.stdout }}"
      when: ansible_os_family != 'Windows'

    - name: Get software version on Windows
      block:
        - name: Query Windows Registry
          win_powershell:
            script: |
              Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* |
              Where-Object {{DisplayName -like '*{software_name}*'}} |
              Select-Object DisplayName, DisplayVersion
          register: win_version

        - name: Show version
          debug:
            msg: "{{ win_version.output }}"
      when: ansible_os_family == 'Windows'
"""

    elif command == "os_info":
        return f"""---
- hosts: {hosts}
  gather_facts: yes
  tasks:
    - name: Display OS Information
      debug:
        msg: |
          Hostname: {{ ansible_hostname }}
          OS: {{ ansible_os_family }} {{ ansible_distribution }} {{ ansible_distribution_version }}
          Kernel: {{ ansible_kernel }}
          Architecture: {{ ansible_architecture }}
          Python: {{ ansible_python_version }}
          Total Memory: {{ ansible_memtotal_mb }} MB
"""

    elif command == "service_status":
        return f"""---
- hosts: {hosts}
  gather_facts: yes
  tasks:
    - name: Get service status on Linux
      block:
        - name: List active services
          shell: |
            systemctl list-units --type=service --state=running --no-pager
          register: service_status
          changed_when: false

        - name: Show status
          debug:
            msg: "{{ service_status.stdout }}"
      when: ansible_os_family != 'Windows'

    - name: Get service status on Windows
      block:
        - name: List Windows services
          win_powershell:
            script: |
              Get-Service | Where-Object {{Status -eq 'Running'}} |
              Select-Object Name, DisplayName, Status |
              Format-Table -AutoSize
          register: win_services

        - name: Show status
          debug:
            msg: "{{ win_services.output }}"
      when: ansible_os_family == 'Windows'
"""

    return None
