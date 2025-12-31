#!/usr/bin/env python3
"""Setup SSH key using paramiko."""

import paramiko
import os
import sys

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

print(f"Connecting to {PI_USER}@{PI_HOST}...")

try:
    # Connect with password
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(PI_HOST, username=PI_USER, password=PI_PASS, timeout=10)
    
    print("Connected! Installing SSH key...")
    
    # Create .ssh directory and install key
    commands = [
        "mkdir -p ~/.ssh",
        "chmod 700 ~/.ssh",
        f'echo "{pubkey}" >> ~/.ssh/authorized_keys',
        "chmod 600 ~/.ssh/authorized_keys",
        "echo 'SSH key installed successfully'"
    ]
    
    for cmd in commands:
        stdin, stdout, stderr = ssh.exec_command(cmd)
        stdout.channel.recv_exit_status()
        output = stdout.read().decode()
        if output:
            print(output.strip())
    
    ssh.close()
    print("\n✓ SSH key installed!")
    
    # Test passwordless connection
    print("\nTesting passwordless SSH...")
    ssh2 = paramiko.SSHClient()
    ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh2.connect(PI_HOST, username=PI_USER, timeout=5)
    stdin, stdout, stderr = ssh2.exec_command("echo 'Passwordless SSH works!'")
    print(stdout.read().decode().strip())
    ssh2.close()
    print("✓ Passwordless SSH is working!")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

