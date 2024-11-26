import threading
import time
import logging

LOG = logging.getLogger(__name__)


class SingletonWithTTL:
    _instances = {}
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        # Ensure thread safety
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__new__(cls)
                cls._instances[cls] = instance
                instance._last_init_time = None
                instance._ttl_seconds = 0
            return cls._instances[cls]

    def init_ttl(self, ttl_seconds=300):
        """Initialize TTL for the singleton instance."""
        self._ttl_seconds = ttl_seconds
        current_time = time.time()

        # Check if reinitialization is needed
        if self._last_init_time is None or (current_time - self._last_init_time > self._ttl_seconds):
            self._last_init_time = current_time
            LOG.info(f"Initializing or reinitializing {self.__class__.__name__} instance.")
            self.on_initialize()
        else:
            LOG.info(
                f"Using existing {self.__class__.__name__} instance. "
                f"Time since last init: {current_time - self._last_init_time:.2f} seconds"
            )

    def on_initialize(self):
        """Placeholder for initialization logic in child classes."""
        raise NotImplementedError("You must implement the `on_initialize` method in the subclass.")

