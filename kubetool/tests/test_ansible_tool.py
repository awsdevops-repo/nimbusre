#!/usr/bin/env python3

import os
import tempfile
from ansible_tool import ansible_tool

def test_ansible_tool():
    """Test the Ansible inventory tool with mock scenarios."""

    print("=" * 60)
    print("Testing Ansible Inventory Tool")
    print("=" * 60)

    # Create a minimal test inventory file
    test_inventory = """[linux_servers]
localhost ansible_connection=local

[windows_servers]
# winhost ansible_connection=winrm ansible_user=admin

[all]
localhost
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
        f.write(test_inventory)
        inventory_path = f.name

    try:
        # Test 1: OS Info
        print("\n🔍 Test 1: Get OS Information")
        print("-" * 60)
        result = ansible_tool(
            command="os_info",
            hosts="localhost",
            inventory_file=inventory_path,
        )
        print(result)

        # Test 2: Software List (if ansible is available)
        print("\n🔍 Test 2: List Installed Software")
        print("-" * 60)
        result = ansible_tool(
            command="software_list",
            hosts="localhost",
            inventory_file=inventory_path,
        )
        print(result)

        # Test 3: Software Version
        print("\n🔍 Test 3: Check Software Version (python)")
        print("-" * 60)
        result = ansible_tool(
            command="software_version",
            hosts="localhost",
            software_name="python",
            inventory_file=inventory_path,
        )
        print(result)

        # Test 4: Service Status
        print("\n🔍 Test 4: Get Service Status")
        print("-" * 60)
        result = ansible_tool(
            command="service_status",
            hosts="localhost",
            inventory_file=inventory_path,
        )
        print(result)

        # Test 5: Error handling - invalid command
        print("\n⚠️  Test 5: Invalid Command (should fail)")
        print("-" * 60)
        result = ansible_tool(
            command="invalid_cmd",
            hosts="localhost",
            inventory_file=inventory_path,
        )
        print(result)

        # Test 6: Error handling - missing software_name
        print("\n⚠️  Test 6: Missing Required Parameter (should fail)")
        print("-" * 60)
        result = ansible_tool(
            command="software_version",
            hosts="localhost",
            inventory_file=inventory_path,
        )
        print(result)

    finally:
        try:
            os.remove(inventory_path)
        except OSError:
            pass

    print("\n" + "=" * 60)
    print("Tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    test_ansible_tool()
