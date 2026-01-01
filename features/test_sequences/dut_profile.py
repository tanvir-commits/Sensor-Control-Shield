"""DUT (Device Under Test) Profile management."""

import json
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict


@dataclass
class DUTProfile:
    """DUT profile configuration."""
    name: str
    uart_port: str
    uart_baud: int = 115200
    gpio_wake: Optional[int] = None
    gpio_reset: Optional[int] = None
    tasks: Dict[str, str] = None  # Task number -> description mapping
    
    def __post_init__(self):
        """Initialize default values."""
        if self.tasks is None:
            self.tasks = {}
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'DUTProfile':
        """Create from dictionary."""
        return cls(**data)


class DUTProfileManager:
    """Manager for DUT profiles."""
    
    def __init__(self, profiles_dir: Optional[Path] = None):
        """Initialize profile manager.
        
        Args:
            profiles_dir: Directory to store profiles (default: ~/.device_panel/profiles)
        """
        if profiles_dir is None:
            profiles_dir = Path.home() / '.device_panel' / 'profiles'
        
        self.profiles_dir = Path(profiles_dir)
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        self.profiles: Dict[str, DUTProfile] = {}
        self.load_all()
        # Create default mock profile if it doesn't exist
        self._ensure_mock_profile()
    
    def load_all(self):
        """Load all profiles from disk."""
        self.profiles = {}
        for profile_file in self.profiles_dir.glob('*.json'):
            try:
                profile = self.load(profile_file.stem)
                if profile:
                    self.profiles[profile.name] = profile
            except Exception as e:
                print(f"Error loading profile {profile_file}: {e}")
    
    def load(self, name: str) -> Optional[DUTProfile]:
        """Load a profile by name.
        
        Args:
            name: Profile name
        
        Returns:
            DUTProfile or None if not found
        """
        profile_file = self.profiles_dir / f"{name}.json"
        if not profile_file.exists():
            return None
        
        try:
            with open(profile_file, 'r') as f:
                data = json.load(f)
            return DUTProfile.from_dict(data)
        except Exception as e:
            print(f"Error loading profile {name}: {e}")
            return None
    
    def save(self, profile: DUTProfile) -> bool:
        """Save a profile.
        
        Args:
            profile: DUTProfile to save
        
        Returns:
            True if saved successfully
        """
        try:
            profile_file = self.profiles_dir / f"{profile.name}.json"
            with open(profile_file, 'w') as f:
                json.dump(profile.to_dict(), f, indent=2)
            
            self.profiles[profile.name] = profile
            return True
        except Exception as e:
            print(f"Error saving profile {profile.name}: {e}")
            return False
    
    def delete(self, name: str) -> bool:
        """Delete a profile.
        
        Args:
            name: Profile name to delete
        
        Returns:
            True if deleted successfully
        """
        try:
            profile_file = self.profiles_dir / f"{name}.json"
            if profile_file.exists():
                profile_file.unlink()
            
            if name in self.profiles:
                del self.profiles[name]
            
            return True
        except Exception as e:
            print(f"Error deleting profile {name}: {e}")
            return False
    
    def list_profiles(self) -> List[str]:
        """List all profile names.
        
        Returns:
            List of profile names
        """
        return list(self.profiles.keys())
    
    def get_profile(self, name: str) -> Optional[DUTProfile]:
        """Get a profile by name.
        
        Args:
            name: Profile name
        
        Returns:
            DUTProfile or None if not found
        """
        return self.profiles.get(name)
    
    def _ensure_mock_profile(self):
        """Ensure a default 'mock' profile exists."""
        if "mock" not in self.profiles:
            mock_profile = DUTProfile(
                name="mock",
                uart_port="/dev/ttyUSB0",
                uart_baud=115200,
                gpio_wake=None,
                gpio_reset=None,
                tasks={
                    "1": "Task 1",
                    "2": "Task 2",
                    "3": "Task 3",
                    "4": "Task 4",
                    "5": "Task 5",
                }
            )
            self.save(mock_profile)
            print("Created default 'mock' profile")

