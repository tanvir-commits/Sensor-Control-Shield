"""Global app manager to ensure only one app runs at a time."""

from typing import Optional, Dict
import threading


class AppManager:
    """Global singleton to manage running apps and ensure only one runs at a time."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._running_app: Optional[object] = None
        self._app_lock = threading.Lock()
        # Ensure no app is running on initialization
        self._running_app = None
    
    def stop_all_apps(self):
        """Stop any currently running app."""
        with self._app_lock:
            if self._running_app is not None:
                try:
                    print(f"AppManager: Stopping app {self._running_app.__class__.__name__}")
                    # Set running to False first to prevent updates
                    if hasattr(self._running_app, 'running'):
                        self._running_app.running = False
                    # Stop the app
                    self._running_app.stop()
                    # Wait for cleanup to complete
                    import time
                    time.sleep(0.2)
                except Exception as e:
                    print(f"AppManager: Error stopping app: {e}")
                finally:
                    self._running_app = None
    
    def register_app(self, app):
        """Register a new app as running. Stops any previous app first."""
        with self._app_lock:
            # Stop any existing app
            self.stop_all_apps()
            # Register new app
            self._running_app = app
            print(f"AppManager: Registered app {app.__class__.__name__}")
    
    def unregister_app(self, app):
        """Unregister an app."""
        with self._app_lock:
            if self._running_app == app:
                self._running_app = None
                print(f"AppManager: Unregistered app {app.__class__.__name__}")
    
    def get_running_app(self):
        """Get the currently running app."""
        return self._running_app

