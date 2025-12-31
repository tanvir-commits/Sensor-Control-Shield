"""Suggestion engine - rules-based app suggestion system."""

from typing import List, Dict, Optional
from dataclasses import dataclass
from .device_detector import DeviceInfo


@dataclass
class Suggestion:
    """An app suggestion based on detected devices."""
    app_name: str
    app_class: str
    description: str
    priority: int
    required_devices: List[str]
    optional_devices: List[str]
    match_score: float  # How well it matches (0.0 to 1.0)


# Suggestion rules - can be extended or loaded from config later
SUGGESTION_RULES = [
    {
        "required": ["IMU", "DISPLAY"],
        "optional": [],
        "app_class": "TiltGameApp",
        "app_name": "Tilt Game",
        "description": "Tilt the board to move a ball on the display",
        "priority": 10,
    },
    {
        "required": ["TEMP_SENSOR", "DISPLAY"],
        "optional": [],
        "app_class": "ThermometerApp",
        "app_name": "Thermometer",
        "description": "Display temperature readings on the display",
        "priority": 8,
    },
    {
        "required": ["DISPLAY"],
        "optional": ["TEMP_SENSOR", "PRESSURE_SENSOR", "IMU"],
        "app_class": "SensorDashboardApp",
        "app_name": "Sensor Dashboard",
        "description": "Display multiple sensor readings",
        "priority": 5,
    },
]


class SuggestionEngine:
    """Rules-based suggestion engine."""
    
    def __init__(self):
        self.rules = SUGGESTION_RULES
    
    def generate_suggestions(self, devices: List[DeviceInfo]) -> List[Suggestion]:
        """Generate app suggestions based on detected devices.
        
        Args:
            devices: List of detected devices
            
        Returns:
            List of Suggestion objects, sorted by priority and match score
        """
        # Extract device categories
        device_categories = set()
        for device in devices:
            if device.category:
                device_categories.add(device.category)
        
        suggestions = []
        
        # Match each rule
        for rule in self.rules:
            required = set(rule["required"])
            optional = set(rule.get("optional", []))
            
            # Check if required categories are present
            if required.issubset(device_categories):
                # Calculate match score
                match_score = self._calculate_match_score(
                    required, optional, device_categories
                )
                
                suggestion = Suggestion(
                    app_name=rule["app_name"],
                    app_class=rule["app_class"],
                    description=rule["description"],
                    priority=rule["priority"],
                    required_devices=list(required),
                    optional_devices=list(optional),
                    match_score=match_score
                )
                suggestions.append(suggestion)
        
        # Sort by priority (higher first), then by match score (higher first)
        suggestions.sort(key=lambda s: (s.priority, s.match_score), reverse=True)
        
        return suggestions
    
    def _calculate_match_score(self, required: set, optional: set, 
                               available: set) -> float:
        """Calculate how well a rule matches available devices.
        
        Args:
            required: Required device categories
            optional: Optional device categories
            available: Available device categories
            
        Returns:
            Match score from 0.0 to 1.0
        """
        # Base score: 1.0 if all required are present
        if not required.issubset(available):
            return 0.0
        
        base_score = 1.0
        
        # Bonus: Add points for optional devices present
        if optional:
            optional_present = optional.intersection(available)
            optional_bonus = len(optional_present) / len(optional)
            # Optional devices add up to 0.2 bonus
            base_score += optional_bonus * 0.2
        
        return min(base_score, 1.0)
    
    def match_rule(self, rule: Dict, device_categories: set) -> bool:
        """Check if a rule matches available device categories.
        
        Args:
            rule: Rule dictionary
            device_categories: Set of available device categories
            
        Returns:
            True if rule matches
        """
        required = set(rule["required"])
        return required.issubset(device_categories)

