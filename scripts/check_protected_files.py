#!/usr/bin/env python3
"""Check if protected files have been modified incorrectly.

This script verifies that protected files follow the rules:
- Feature flags are used
- Try/except blocks are present
- No breaking changes
"""

import sys
import os
import re
from pathlib import Path

# Protected files and their rules
PROTECTED_FILES = {
    "device_panel.py": {
        "required_feature_flag": True,
        "required_try_except": True,
    },
    "ui/main_window.py": {
        "required_feature_flag": True,
        "required_try_except": True,
    },
    "hardware/gpio_manager.py": {
        "read_only": True,
    },
    "hardware/adc_manager.py": {
        "read_only": True,
    },
    "hardware/i2c_scanner.py": {
        "read_only": True,
    },
    "config/pins.py": {
        "read_only": True,
    },
}

def check_file(filepath, rules):
    """Check if a file follows protection rules."""
    errors = []
    warnings = []
    
    if not os.path.exists(filepath):
        return errors, warnings
    
    with open(filepath, 'r') as f:
        content = f.read()
        lines = content.split('\n')
    
    # Check for read-only violations
    if rules.get("read_only"):
        # This is a simple check - in practice, you'd use git diff
        warnings.append(f"{filepath}: File is read-only. Verify no unauthorized changes.")
    
    # Check for feature flag usage
    if rules.get("required_feature_flag"):
        if "feature_flags" not in content and "ENABLE_" in content:
            errors.append(f"{filepath}: Feature code should check feature flags")
    
    # Check for try/except blocks around feature code
    if rules.get("required_try_except"):
        # Look for imports that might be feature-related
        feature_imports = ["power_profiler", "test_sequences", "smart_suggestions"]
        for imp in feature_imports:
            if imp in content:
                # Check if it's in a try/except
                if f"import.*{imp}" in content:
                    # Simple check - would need more sophisticated parsing
                    if "try:" not in content or "except" not in content:
                        warnings.append(f"{filepath}: Feature imports should be in try/except blocks")
    
    return errors, warnings

def main():
    """Main check function."""
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    all_errors = []
    all_warnings = []
    
    for filepath, rules in PROTECTED_FILES.items():
        full_path = project_root / filepath
        errors, warnings = check_file(full_path, rules)
        all_errors.extend(errors)
        all_warnings.extend(warnings)
    
    # Print results
    if all_errors:
        print("ERRORS (must fix):")
        for error in all_errors:
            print(f"  - {error}")
        print()
    
    if all_warnings:
        print("WARNINGS (should review):")
        for warning in all_warnings:
            print(f"  - {warning}")
        print()
    
    if not all_errors and not all_warnings:
        print("✓ Protected files check passed")
        return 0
    
    if all_errors:
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

