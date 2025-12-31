#!/usr/bin/env python3
"""Setup SSH key on remote Pi."""

import subprocess
import sys
import os

PI_HOST = "192.168.101"
PI_USER = "a"
PI_PASS = "1"

# Read public key
pubkey_path = os.path.expanduser("~/.ssh/id_ed25519.pub")
if not os.path.exists(pubkey_path):
    pubkey_path = os.path.expanduser("~/.ssh/id_rsa.pub")

if not os.path.exists(pubkey_path):
    print("Error: No SSH public key found")
    sys.exit(1)

with open(pubkey_path, 'r') as f:
    pubkey = f.read().strip()

print(f"Installing SSH key to {PI_USER}@{PI_HOST}...")

# Use sshpass to copy key
cmd = f"""sshpass -p '{PI_PASS}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {PI_USER}@{PI_HOST} 'mkdir -p ~/.ssh && echo "{pubkey}" >> ~/.ssh/authorized_keys && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys && echo "Key installed"'"""

result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

if result.returncode == 0:
    print("SSH key installed successfully!")
    print(result.stdout)
    
    # Test passwordless connection
    print("\nTesting passwordless SSH...")
    test_cmd = f"ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 {PI_USER}@{PI_HOST} 'echo SSH key authentication works!'"
    test_result = subprocess.run(test_cmd, shell=True, capture_output=True, text=True)
    
    if test_result.returncode == 0:
        print("✓ Passwordless SSH is working!")
        print(test_result.stdout)
        sys.exit(0)
    else:
        print("⚠ SSH key installed but passwordless connection failed")
        print(test_result.stderr)
        sys.exit(1)
else:
    print("Error installing SSH key:")
    print(result.stderr)
    sys.exit(1)

