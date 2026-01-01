"""Results and reporting system for QA test sequences."""

import json
import csv
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from .qa_engine import SequenceResult, StepResult


class ResultsManager:
    """Manager for sequence execution results."""
    
    def __init__(self, results_dir: Optional[Path] = None):
        """Initialize results manager.
        
        Args:
            results_dir: Directory to store results (default: ~/.device_panel/results)
        """
        if results_dir is None:
            results_dir = Path.home() / '.device_panel' / 'results'
        
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.results: List[SequenceResult] = []
    
    def add_result(self, result: SequenceResult):
        """Add a result to the manager.
        
        Args:
            result: SequenceResult to add
        """
        self.results.append(result)
    
    def save_result(self, result: SequenceResult, format: str = 'json') -> bool:
        """Save a result to disk.
        
        Args:
            result: SequenceResult to save
            format: Format ('json' or 'csv')
        
        Returns:
            True if saved successfully
        """
        timestamp = result.start_time.strftime('%Y%m%d_%H%M%S')
        filename = f"{result.sequence_name}_{timestamp}.{format}"
        filepath = self.results_dir / filename
        
        try:
            if format == 'json':
                return self._save_json(result, filepath)
            elif format == 'csv':
                return self._save_csv(result, filepath)
            else:
                print(f"Unknown format: {format}")
                return False
        except Exception as e:
            print(f"Error saving result: {e}")
            return False
    
    def _save_json(self, result: SequenceResult, filepath: Path) -> bool:
        """Save result as JSON.
        
        Args:
            result: SequenceResult to save
            filepath: File path
        
        Returns:
            True if saved successfully
        """
        data = {
            'sequence_name': result.sequence_name,
            'status': result.status.value,
            'start_time': result.start_time.isoformat(),
            'end_time': result.end_time.isoformat() if result.end_time else None,
            'total_duration': result.total_duration,
            'pass_count': result.pass_count,
            'fail_count': result.fail_count,
            'error_message': result.error_message,
            'steps': [
                {
                    'type': step.step.type.value,
                    'params': step.step.params,
                    'success': step.success,
                    'message': step.message,
                    'duration': step.duration,
                    'timestamp': step.timestamp.isoformat(),
                    'data': step.data
                }
                for step in result.step_results
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        return True
    
    def _save_csv(self, result: SequenceResult, filepath: Path) -> bool:
        """Save result as CSV.
        
        Args:
            result: SequenceResult to save
            filepath: File path
        
        Returns:
            True if saved successfully
        """
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow(['Sequence Result'])
            writer.writerow(['Sequence Name', result.sequence_name])
            writer.writerow(['Status', result.status.value])
            writer.writerow(['Start Time', result.start_time.isoformat()])
            writer.writerow(['End Time', result.end_time.isoformat() if result.end_time else ''])
            writer.writerow(['Total Duration', f"{result.total_duration:.3f}s"])
            writer.writerow(['Pass Count', result.pass_count])
            writer.writerow(['Fail Count', result.fail_count])
            writer.writerow(['Error Message', result.error_message])
            writer.writerow([])
            
            # Steps
            writer.writerow(['Steps'])
            writer.writerow(['Index', 'Type', 'Success', 'Message', 'Duration (s)', 'Timestamp'])
            for i, step in enumerate(result.step_results):
                writer.writerow([
                    i + 1,
                    step.step.type.value,
                    'PASS' if step.success else 'FAIL',
                    step.message,
                    f"{step.duration:.3f}",
                    step.timestamp.isoformat()
                ])
        
        return True
    
    def load_result(self, filepath: Path) -> Optional[SequenceResult]:
        """Load a result from disk.
        
        Args:
            filepath: File path to load from
        
        Returns:
            SequenceResult or None if error
        """
        # This would require implementing from_dict methods
        # For now, just return None - can be implemented if needed
        return None
    
    def list_results(self) -> List[Path]:
        """List all result files.
        
        Returns:
            List of result file paths
        """
        json_files = list(self.results_dir.glob('*.json'))
        csv_files = list(self.results_dir.glob('*.csv'))
        return sorted(json_files + csv_files, reverse=True)  # Most recent first
    
    def get_summary(self) -> dict:
        """Get summary of all results.
        
        Returns:
            Dictionary with summary statistics
        """
        if not self.results:
            return {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'total_duration': 0.0
            }
        
        passed = sum(1 for r in self.results if r.is_passed())
        failed = len(self.results) - passed
        total_duration = sum(r.total_duration for r in self.results)
        
        return {
            'total': len(self.results),
            'passed': passed,
            'failed': failed,
            'total_duration': total_duration,
            'average_duration': total_duration / len(self.results) if self.results else 0.0
        }


