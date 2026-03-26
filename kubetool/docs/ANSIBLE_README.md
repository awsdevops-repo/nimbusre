# Ansible Software Inventory Tool

A LangChain-based tool for querying installed software versions and system information across Linux and Windows hosts using Ansible.

## Overview

The **Ansible Inventory Tool** provides a secure, restricted interface to query software inventory across hybrid Linux and Windows environments. It's designed to work with LangChain agents and supports:

- **Software listing** - Get all installed packages (apt, yum, dnf on Linux; WMI on Windows)
- **Version checking** - Query specific software versions
- **OS information** - Gather system details (OS, kernel, memory, etc.)
- **Service status** - List running services

## Features

✅ **Safe by default** - Restricted to read-only operations (no destructive commands)  
✅ **Multi-platform** - Supports Debian, RHEL/CentOS, Windows  
✅ **LangChain integration** - Works with AI agents for natural language queries  
✅ **SSH key support** - Securely connects using SSH keys (no passwords in code)  
✅ **Input validation** - Pydantic schemas enforce allowed operations  

## Setup

### Prerequisites

```bash
# Install Ansible
pip install ansible

# Install LangChain dependencies (if using agent)
pip install langchain-ollama langchain-core

# SSH keys for Linux hosts
ssh-keygen -t ed25519 -f ~/.ssh/ansible-key.pem

# For Windows: Enable WinRM (PowerShell admin)
# winrm quickconfig -q
```

### Configuration

1. **Create inventory file** (e.g., `ansible_inventory.yaml`):

```yaml
[linux_servers]
ubuntu-01 ansible_host=192.168.1.10 ansible_user=ubuntu
rhel-01 ansible_host=192.168.1.20 ansible_user=ec2-user

[windows_servers]
winserver-01 ansible_host=192.168.1.30 ansible_user=Administrator

[all:vars]
ansible_ssh_private_key_file=~/.ssh/ansible-key.pem
```

2. **Test connectivity**:

```bash
ansible all -i ansible_inventory.yaml -m ping
```

## Usage

### Direct Tool Usage

```python
from ansible_tool import ansible_tool

# List all software on Linux servers
result = ansible_tool(
    command="software_list",
    hosts="linux_servers",
    inventory_file="ansible_inventory.yaml"
)
print(result)

# Check Python version
result = ansible_tool(
    command="software_version",
    hosts="ubuntu-01",
    software_name="python3",
    inventory_file="ansible_inventory.yaml"
)
print(result)

# Get OS information
result = ansible_tool(
    command="os_info",
    hosts="all",
    inventory_file="ansible_inventory.yaml"
)
print(result)
```

### With LangChain Agent

```python
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from ansible_tool import ansible_tool

# Create agent with the tool
llm = ChatOllama(model="llama3.1", temperature=0).bind_tools([ansible_tool])
agent = create_agent(llm, tools=[ansible_tool])

# Query in natural language
result = agent.invoke({
    "messages": [("human", "What version of Python is installed on ubuntu servers?")]
})
print(result['messages'][-1].content)
```

## API Reference

### Commands

| Command | Description | Required Args |
|---------|-------------|---|
| `software_list` | List all installed packages | `hosts` |
| `software_version` | Get specific software version | `hosts`, `software_name` |
| `os_info` | Show OS and system information | `hosts` |
| `service_status` | List running services | `hosts` |

### Parameters

- **command** (str): One of the allowed commands above
- **hosts** (str): Ansible host pattern (e.g., "all", "linux_servers", "ubuntu-01")
- **software_name** (str, optional): Package name for version queries
- **inventory_file** (str, optional): Path to inventory file (defaults to `~/.ansible/hosts`)
- **extra_vars** (dict, optional): Additional Ansible variables

## Testing

```bash
# Test with local host
python test_ansible_tool.py

# Test with real inventory
python test_ansible_tool.py --inventory ansible_inventory.yaml

# Run agent interactively
python ansible_agent.py
```

## Security Considerations

⚠️ **Command Restrictions**
- Only read-only operations are allowed
- No `apply`, `delete`, `patch`, `edit`, `exec` commands
- No vault or interactive password prompts
- Kubeconfig files cannot be passed directly

✅ **Best Practices**
- Use SSH key authentication (avoid passwords)
- Store `ansible_inventory.yaml` outside version control
- Use Ansible vaults for sensitive variables
- Limit agent access to specific host groups
- Audit playbook logs for compliance

## Examples

### Query all software with versions

```python
result = ansible_tool(
    command="software_list",
    hosts="prod",
    inventory_file="ansible_inventory.yaml"
)
# Returns: dpkg/rpm package lists with versions
```

### Check Docker installation on Windows

```python
result = ansible_tool(
    command="software_version",
    hosts="windows_servers",
    software_name="Docker",
    inventory_file="ansible_inventory.yaml"
)
# Returns: Windows Registry entries for Docker
```

### Get system info for compliance audits

```python
result = ansible_tool(
    command="os_info",
    hosts="all",
    inventory_file="ansible_inventory.yaml"
)
# Returns: OS version, kernel, architecture for all hosts
```

## Troubleshooting

### "Inventory file not found"
Ensure the inventory file path is correct and readable.

### "ansible-playbook not found"
Install Ansible: `pip install ansible`

### Permission denied on Linux hosts
Check SSH key permissions: `chmod 600 ~/.ssh/ansible-key.pem`
Verify SSH connectivity: `ssh -i ~/.ssh/ansible-key.pem user@host`

### Windows WinRM errors
Enable WinRM on Windows hosts (run as Administrator):
```powershell
winrm quickconfig -q
Set-NetConnectionProfile -Name "Public" -NetworkCategory "Private"
```

## Integration with SREAgent

This tool is part of the **SREAgent** project for:
- ✅ Software version checks
- ✅ Software upgrades/patches (future)
- ✅ Infrastructure diagnostics

See `REquirements_hackathon.txt` for full SREAgent scope.
