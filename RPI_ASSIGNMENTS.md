# Raspberry Pi Assignments

Quick reference for RPi assignments and connection details.

## RPi 1 - Smart Suggestions Testing

**IP Address**: 192.168.101  
**Username**: `a`  
**Password**: `1`  
**Branch**: `feature/smart-suggestions`  
**Purpose**: Automatic app suggestion feature testing

### Connection

```bash
# SSH connection
ssh a@192.168.101

# Deploy branch
./scripts/deploy-to-pi.sh -b feature/smart-suggestions -h 192.168.101 -u a

# Initial setup (first time)
./scripts/setup-pi-for-branch.sh -h 192.168.101 -b feature/smart-suggestions -u a
```

### Notes

- Used for testing smart suggestions feature
- Tests device detection and app suggestions
- Requires I2C sensors and displays for testing

---

## RPi 2 - Power Profiler Testing

**IP Address**: 192.168.102  
**Username**: `pi` (verify if different)  
**Password**: (verify)  
**Branch**: `feature/power-profiler`  
**Purpose**: Power profiler feature testing

### Connection

```bash
# SSH connection
ssh pi@192.168.102

# Deploy branch
./scripts/deploy-to-pi.sh -b feature/power-profiler -h 192.168.102 -u pi

# Initial setup (first time)
./scripts/setup-pi-for-branch.sh -h 192.168.102 -b feature/power-profiler -u pi
```

### Notes

- Used for testing power profiler feature
- Tests INA260 current sensors
- Tests power measurement and sequences
- Requires INA260 sensors and test hardware

---

## Future Assignments

- **RPi 3+**: For `feature/test-sequences` or `dev` integration testing
- **Additional RPis**: As needed for parallel testing

---

## Quick Deployment Commands

### Smart Suggestions (RPi 1)

```bash
# Deploy updates
./scripts/deploy-to-pi.sh -b feature/smart-suggestions -h 192.168.101 -u a

# Run app on RPi
ssh a@192.168.101 "cd /opt/device-panel && python3 device_panel.py"
```

### Power Profiler (RPi 2)

```bash
# Deploy updates
./scripts/deploy-to-pi.sh -b feature/power-profiler -h 192.168.102 -u pi

# Run app on RPi
ssh pi@192.168.102 "cd /opt/device-panel && python3 device_panel.py"
```

---

## Troubleshooting

### Connection Issues

1. **Can't connect via SSH**:
   - Verify RPi is powered on
   - Check network connectivity: `ping 192.168.101` or `ping 192.168.102`
   - Verify SSH is enabled on RPi
   - Check firewall settings

2. **Authentication fails**:
   - Verify username and password
   - Try passwordless SSH key setup
   - Check SSH key permissions

3. **Deployment fails**:
   - Verify git repository exists on RPi
   - Check directory permissions
   - Verify Python dependencies are installed

### Setup Issues

1. **First time setup**:
   - Run `setup-pi-for-branch.sh` first
   - Then use `deploy-to-pi.sh` for updates

2. **Dependencies missing**:
   - SSH to RPi and run: `pip3 install -r requirements.txt`
   - Or run setup script again

---

## Notes

- Update this file if assignments change
- Document any special configuration needed
- Keep connection details secure (don't commit passwords if sensitive)

