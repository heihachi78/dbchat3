import asyncio
import time
import logging
import random
from functools import wraps
from typing import Callable, Any, Union, Tuple, Type
from openai import RateLimitError, APIConnectionError, APITimeoutError

logger = logging.getLogger(__name__)

class RetryError(Exception):
    """Raised when all retry attempts have been exhausted"""
    def __init__(self, original_error: Exception, attempts: int):
        self.original_error = original_error
        self.attempts = attempts
        super().__init__(f"Failed after {attempts} attempts: {original_error}")

def calculate_backoff_delay(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0, jitter: bool = True) -> float:
    """Calculate exponential backoff delay with optional jitter"""
    delay = min(base_delay * (2 ** attempt), max_delay)
    if jitter:
        delay = delay * (0.5 + random.random() * 0.5)  # Add 0-50% jitter
    return delay

def retry_sync(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_multiplier: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """Decorator for synchronous functions with retry logic"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # Check if this exception type should be retried
                    if not isinstance(e, retryable_exceptions):
                        logger.error(f"{func.__name__} failed with non-retryable error: {e}")
                        raise
                    
                    if attempt == max_attempts - 1:
                        logger.error(f"{func.__name__} failed after {max_attempts} attempts: {e}")
                        raise RetryError(e, max_attempts)
                    
                    delay = calculate_backoff_delay(attempt, base_delay, max_delay, jitter)
                    logger.warning(f"{func.__name__} attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f}s...")
                    time.sleep(delay)
            
            # This should never be reached, but just in case
            raise RetryError(last_exception, max_attempts)
        
        return wrapper
    return decorator

def retry_async(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_multiplier: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """Decorator for async functions with retry logic"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # Check if this exception type should be retried
                    if not isinstance(e, retryable_exceptions):
                        logger.error(f"{func.__name__} failed with non-retryable error: {e}")
                        raise
                    
                    if attempt == max_attempts - 1:
                        logger.error(f"{func.__name__} failed after {max_attempts} attempts: {e}")
                        raise RetryError(e, max_attempts)
                    
                    delay = calculate_backoff_delay(attempt, base_delay, max_delay, jitter)
                    logger.warning(f"{func.__name__} attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f}s...")
                    await asyncio.sleep(delay)
            
            # This should never be reached, but just in case
            raise RetryError(last_exception, max_attempts)
        
        return wrapper
    return decorator

# Specific retry configurations for different operation types
AZURE_API_RETRY_CONFIG = {
    'max_attempts': 3,
    'base_delay': 1.0,
    'max_delay': 30.0,
    'retryable_exceptions': (RateLimitError, APIConnectionError, APITimeoutError, ConnectionError)
}

DATABASE_RETRY_CONFIG = {
    'max_attempts': 3,
    'base_delay': 2.0,
    'max_delay': 60.0,
    'retryable_exceptions': (ConnectionError, TimeoutError, OSError)
}

FILE_OPERATION_RETRY_CONFIG = {
    'max_attempts': 2,
    'base_delay': 0.5,
    'max_delay': 5.0,
    'retryable_exceptions': (OSError, IOError, PermissionError)
}

class CircuitBreaker:
    """Simple circuit breaker pattern implementation"""
    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        if self.state == "open":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half-open"
                logger.info("Circuit breaker moving to half-open state")
            else:
                raise Exception("Circuit breaker is open - operation blocked")
        
        try:
            result = func(*args, **kwargs)
            if self.state == "half-open":
                self.state = "closed"
                self.failure_count = 0
                logger.info("Circuit breaker closed - operation successful")
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
                logger.error(f"Circuit breaker opened after {self.failure_count} failures")
            
            raise

    async def call_async(self, func: Callable, *args, **kwargs) -> Any:
        """Execute async function with circuit breaker protection"""
        if self.state == "open":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half-open"
                logger.info("Circuit breaker moving to half-open state")
            else:
                raise Exception("Circuit breaker is open - operation blocked")
        
        try:
            result = await func(*args, **kwargs)
            if self.state == "half-open":
                self.state = "closed"
                self.failure_count = 0
                logger.info("Circuit breaker closed - operation successful")
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
                logger.error(f"Circuit breaker opened after {self.failure_count} failures")
            
            raise