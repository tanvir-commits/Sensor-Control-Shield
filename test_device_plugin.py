#!/usr/bin/env python3
"""Quick test script for device plugin functionality."""

import sys
sys.path.insert(0, '/opt/device-panel')

from devices.loader import get_loader
from hardware.adc_manager import ADCManager

print("=" * 60)
print("Testing Device Plugin - ADS1115")
print("=" * 60)

# Test ADC manager directly
print("\n1. Testing ADC Manager:")
adc = ADCManager()
if adc.adc:
    print("   ✓ ADC initialized successfully")
    readings = adc.read_all_channels()
    print(f"   ✓ Readings: {readings}")
else:
    print("   ⚠ ADC not initialized (using mock)")
    readings = adc.read_all_channels()
    print(f"   Mock readings: {readings}")

# Test plugin creation
print("\n2. Testing Plugin Creation:")
loader = get_loader()
device = loader.create_device(1, 0x48, 'ads1115')

if device:
    print("   ✓ Plugin created successfully")
    print(f"   Device: {device.name} at 0x{device.address:02X}")
    
    # Test info
    print("\n3. Testing Device Info:")
    info = device.get_info()
    for key, value in info.items():
        print(f"   {key}: {value}")
    
    # Test detection
    print("\n4. Testing Device Detection:")
    try:
        detected = device.detect()
        print(f"   Detection result: {'✓ Detected' if detected else '✗ Not detected'}")
    except Exception as e:
        print(f"   Detection error: {e}")
    
    # Test reading via hardware (if we can access it)
    print("\n5. Testing ADC Reading (via plugin):")
    # Set hardware reference
    class MockHardware:
        def __init__(self):
            self.adc = adc
    
    device.set_hardware(MockHardware())
    
    # Try to read - this would normally be done via the test UI button
    print("   Note: Full test UI requires GUI interaction")
    print("   But ADC manager is working:", "✓" if adc.adc else "⚠ (mock)")
    
else:
    print("   ✗ Failed to create plugin")

print("\n" + "=" * 60)
print("Test complete!")
print("=" * 60)

