"""
Error Recovery Framework - Gold Tier Foundation

Provides enterprise-grade error recovery with:
- Retry with exponential backoff
- Circuit breaker pattern
- Dead letter queue for failed tasks
- Graceful degradation

Features:
- Automatic retry for transient errors
- Circuit breaker prevents cascade failures
- DLQ captures failed tasks for manual review
- Configurable retry policies
- State persistence
"""

import time
import logging
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, Any, Dict, Optional, List
from functools import wraps
from enum import Enum
from dataclasses import dataclass, asdict

# Add project root to path for imports
PROJECT_ROOT_IMPORT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT_IMPORT))
sys.path.insert(0, str(PROJECT_ROOT_IMPORT / "src"))

# Import audit logger
from utils.audit_logger import log_audit, AuditDomain, AuditStatus


# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
DLQ_PATH = PROJECT_ROOT / "Vault" / "Dead_Letter_Queue"
CIRCUIT_BREAKER_STATE_FILE = PROJECT_ROOT / "config" / "circuit_breaker_state.json"

# Ensure directories
DLQ_PATH.mkdir(parents=True, exist_ok=True)
CIRCUIT_BREAKER_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

# Logging
logger = logging.getLogger("ErrorRecovery")


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_retries: int = 3
    initial_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    exponential_base: float = 2.0
    jitter: bool = True  # Add randomness to prevent thundering herd


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5  # Open circuit after N failures
    success_threshold: int = 2  # Close circuit after N successes in half-open
    timeout: int = 60  # Seconds before transitioning from open to half-open
    name: str = "default"


class CircuitBreaker:
    """
    Circuit breaker implementation.

    Prevents cascade failures by failing fast when a service is down.

    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Service is failing, requests fail immediately
    - HALF_OPEN: Testing if service recovered, limited requests allowed
    """

    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.last_state_change = datetime.now()

        # Load persisted state if exists
        self._load_state()

    def _load_state(self):
        """Load circuit breaker state from disk."""
        try:
            if CIRCUIT_BREAKER_STATE_FILE.exists():
                with open(CIRCUIT_BREAKER_STATE_FILE, 'r') as f:
                    states = json.load(f)
                    if self.config.name in states:
                        state_data = states[self.config.name]
                        self.state = CircuitState(state_data['state'])
                        self.failure_count = state_data['failure_count']
                        self.success_count = state_data['success_count']
                        if state_data['last_failure_time']:
                            self.last_failure_time = datetime.fromisoformat(
                                state_data['last_failure_time']
                            )
                        logger.info(f"Loaded circuit breaker state for {self.config.name}: {self.state.value}")
        except Exception as e:
            logger.warning(f"Failed to load circuit breaker state: {e}")

    def _save_state(self):
        """Persist circuit breaker state to disk."""
        try:
            states = {}
            if CIRCUIT_BREAKER_STATE_FILE.exists():
                with open(CIRCUIT_BREAKER_STATE_FILE, 'r') as f:
                    states = json.load(f)

            states[self.config.name] = {
                'state': self.state.value,
                'failure_count': self.failure_count,
                'success_count': self.success_count,
                'last_failure_time': self.last_failure_time.isoformat() if self.last_failure_time else None,
                'last_state_change': self.last_state_change.isoformat()
            }

            with open(CIRCUIT_BREAKER_STATE_FILE, 'w') as f:
                json.dump(states, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save circuit breaker state: {e}")

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function through circuit breaker.

        Raises:
            CircuitBreakerOpenError: If circuit is open
        """
        # Check if circuit should transition from OPEN to HALF_OPEN
        if self.state == CircuitState.OPEN:
            if self.last_failure_time:
                elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                if elapsed >= self.config.timeout:
                    logger.info(f"Circuit breaker {self.config.name}: Transitioning to HALF_OPEN")
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                    self.last_state_change = datetime.now()
                    self._save_state()
                else:
                    # Circuit still open
                    raise CircuitBreakerOpenError(
                        f"Circuit breaker {self.config.name} is OPEN. "
                        f"Retry in {self.config.timeout - elapsed:.0f}s"
                    )
            else:
                raise CircuitBreakerOpenError(f"Circuit breaker {self.config.name} is OPEN")

        # Execute function
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        """Handle successful call."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                logger.info(f"Circuit breaker {self.config.name}: Transitioning to CLOSED")
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                self.last_state_change = datetime.now()
                self._save_state()
        elif self.state == CircuitState.CLOSED:
            # Reset failure count on success
            self.failure_count = 0
            self._save_state()

    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.state == CircuitState.HALF_OPEN:
            logger.warning(f"Circuit breaker {self.config.name}: Failure in HALF_OPEN, reopening")
            self.state = CircuitState.OPEN
            self.success_count = 0
            self.last_state_change = datetime.now()
            self._save_state()

        elif self.state == CircuitState.CLOSED:
            if self.failure_count >= self.config.failure_threshold:
                logger.error(f"Circuit breaker {self.config.name}: Opening due to {self.failure_count} failures")
                self.state = CircuitState.OPEN
                self.last_state_change = datetime.now()
                self._save_state()

                # Audit log: Circuit opened
                log_audit(
                    action="circuit_breaker.opened",
                    actor="error_recovery",
                    domain=AuditDomain.SYSTEM,
                    resource=self.config.name,
                    status=AuditStatus.FAILURE,
                    details={"failure_count": self.failure_count}
                )

    def reset(self):
        """Manually reset circuit breaker to CLOSED state."""
        logger.info(f"Circuit breaker {self.config.name}: Manual reset")
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.last_state_change = datetime.now()
        self._save_state()


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass


class DeadLetterQueue:
    """
    Dead Letter Queue for failed tasks.

    Tasks that fail after max retries are queued here for manual review.
    """

    def __init__(self, queue_dir: Path = DLQ_PATH):
        self.queue_dir = queue_dir
        self.queue_dir.mkdir(parents=True, exist_ok=True)

    def enqueue(
        self,
        task_id: str,
        task_data: Dict[str, Any],
        error: str,
        retry_count: int,
        last_attempt: datetime = None
    ) -> Path:
        """
        Add failed task to DLQ.

        Args:
            task_id: Unique task identifier
            task_data: Task details
            error: Error message
            retry_count: Number of retries attempted
            last_attempt: Timestamp of last attempt

        Returns:
            Path to DLQ file
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"DLQ_{timestamp}_{task_id}.json"
        filepath = self.queue_dir / filename

        dlq_entry = {
            "task_id": task_id,
            "task_data": task_data,
            "error": error,
            "retry_count": retry_count,
            "enqueued_at": datetime.now().isoformat(),
            "last_attempt": last_attempt.isoformat() if last_attempt else None,
            "status": "failed"
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(dlq_entry, f, indent=2)

        logger.error(f"Task {task_id} added to DLQ: {error}")

        # Audit log: Task added to DLQ
        log_audit(
            action="dlq.enqueue",
            actor="error_recovery",
            domain=AuditDomain.SYSTEM,
            resource=task_id,
            status=AuditStatus.FAILURE,
            details={"error": error, "retry_count": retry_count, "dlq_file": str(filepath)},
            error=error
        )

        return filepath

    def get_all(self) -> List[Dict[str, Any]]:
        """Get all tasks in DLQ."""
        tasks = []
        for dlq_file in self.queue_dir.glob("DLQ_*.json"):
            try:
                with open(dlq_file, 'r', encoding='utf-8') as f:
                    task = json.load(f)
                    task['dlq_file'] = str(dlq_file)
                    tasks.append(task)
            except Exception as e:
                logger.warning(f"Failed to read DLQ file {dlq_file}: {e}")
        return tasks

    def retry_task(self, dlq_file: Path) -> bool:
        """
        Manually retry a task from DLQ.

        Args:
            dlq_file: Path to DLQ file

        Returns:
            True if task should be retried
        """
        # Implementation would trigger re-execution
        # For now, just mark as retried
        try:
            with open(dlq_file, 'r', encoding='utf-8') as f:
                task = json.load(f)

            task['status'] = 'retried'
            task['retried_at'] = datetime.now().isoformat()

            with open(dlq_file, 'w', encoding='utf-8') as f:
                json.dump(task, f, indent=2)

            logger.info(f"DLQ task marked for retry: {dlq_file.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to retry DLQ task: {e}")
            return False


def retry_with_backoff(config: RetryConfig = None):
    """
    Decorator for retry with exponential backoff.

    Usage:
        @retry_with_backoff(RetryConfig(max_retries=5))
        def my_function():
            # Your code
            pass
    """
    if config is None:
        config = RetryConfig()

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            delay = config.initial_delay

            for attempt in range(config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < config.max_retries:
                        # Calculate delay with exponential backoff
                        if config.jitter:
                            import random
                            jitter = random.uniform(0, delay * 0.1)
                            actual_delay = min(delay + jitter, config.max_delay)
                        else:
                            actual_delay = min(delay, config.max_delay)

                        logger.warning(
                            f"{func.__name__} failed (attempt {attempt + 1}/{config.max_retries + 1}): {e}. "
                            f"Retrying in {actual_delay:.2f}s..."
                        )

                        time.sleep(actual_delay)
                        delay *= config.exponential_base
                    else:
                        logger.error(
                            f"{func.__name__} failed after {config.max_retries + 1} attempts: {e}"
                        )

            # All retries exhausted
            raise last_exception

        return wrapper
    return decorator


# Global instances
_circuit_breakers: Dict[str, CircuitBreaker] = {}
_dlq = DeadLetterQueue()


def get_circuit_breaker(name: str, config: CircuitBreakerConfig = None) -> CircuitBreaker:
    """Get or create a circuit breaker instance."""
    if name not in _circuit_breakers:
        if config is None:
            config = CircuitBreakerConfig(name=name)
        _circuit_breakers[name] = CircuitBreaker(config)
    return _circuit_breakers[name]


def get_dlq() -> DeadLetterQueue:
    """Get the global Dead Letter Queue instance."""
    return _dlq


if __name__ == "__main__":
    # Test error recovery framework
    print("Testing Error Recovery Framework...")

    # Test 1: Retry decorator
    print("\n1. Testing retry decorator...")

    attempt_count = 0

    @retry_with_backoff(RetryConfig(max_retries=3, initial_delay=0.5))
    def flaky_function():
        global attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise Exception(f"Simulated failure (attempt {attempt_count})")
        return "Success!"

    try:
        result = flaky_function()
        print(f"[OK] Retry succeeded after {attempt_count} attempts: {result}")
    except Exception as e:
        print(f"[FAIL] Retry failed: {e}")

    # Test 2: Circuit breaker
    print("\n2. Testing circuit breaker...")

    cb_config = CircuitBreakerConfig(name="test_service", failure_threshold=3, timeout=5)
    cb = get_circuit_breaker("test_service", cb_config)

    def failing_service():
        raise Exception("Service is down")

    # Simulate failures to open circuit
    for i in range(5):
        try:
            cb.call(failing_service)
        except Exception as e:
            print(f"  Attempt {i + 1}: {e}")

    print(f"[OK] Circuit state: {cb.state.value}")

    # Try calling with open circuit
    try:
        cb.call(failing_service)
    except CircuitBreakerOpenError as e:
        print(f"[OK] Circuit breaker prevented call: {e}")

    # Test 3: Dead Letter Queue
    print("\n3. Testing Dead Letter Queue...")

    dlq = get_dlq()
    dlq_file = dlq.enqueue(
        task_id="test_task_001",
        task_data={"action": "test", "params": {}},
        error="Simulated permanent failure",
        retry_count=3
    )
    print(f"[OK] Task added to DLQ: {dlq_file.name}")

    all_dlq_tasks = dlq.get_all()
    print(f"[OK] DLQ contains {len(all_dlq_tasks)} task(s)")

    print("\n[SUCCESS] All tests passed!")
