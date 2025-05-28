import logging
import time
from datetime import datetime
from typing import Optional, Dict, Any
from contextlib import contextmanager

# Configure a specific logger for progress tracking
progress_logger = logging.getLogger('progress')
progress_logger.setLevel(logging.INFO)

# Create a console handler with a specific format for progress
if not progress_logger.handlers:
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - PROGRESS - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    progress_logger.addHandler(console_handler)


class SimpleProgress:
    """Simple progress tracking with logging - no complex state management."""
    
    def __init__(self, name: str, total_items: int):
        self.name = name
        self.total_items = total_items
        self.completed_items = 0
        self.start_time = time.time()
        self.last_log_time = self.start_time
        self.log_interval = 10  # Log every 10 seconds or 10% progress
        
        progress_logger.info(f"Starting: {name} (0/{total_items} items)")
    
    def update(self, completed: Optional[int] = None, increment: int = 1):
        """Update progress and log if needed."""
        if completed is not None:
            self.completed_items = completed
        else:
            self.completed_items += increment
        
        # Log progress every 10% or every 10 seconds
        current_time = time.time()
        progress_percent = (self.completed_items / self.total_items) * 100
        
        should_log = (
            current_time - self.last_log_time >= self.log_interval or
            self.completed_items % max(1, self.total_items // 10) == 0 or
            self.completed_items == self.total_items
        )
        
        if should_log:
            elapsed = current_time - self.start_time
            rate = self.completed_items / elapsed if elapsed > 0 else 0
            eta = (self.total_items - self.completed_items) / rate if rate > 0 else 0
            
            progress_logger.info(
                f"{self.name}: {self.completed_items}/{self.total_items} "
                f"({progress_percent:.1f}%) - {rate:.1f} items/sec - "
                f"ETA: {eta/60:.1f}min"
            )
            self.last_log_time = current_time
    
    def complete(self, success: bool = True, message: str = ""):
        """Mark as complete and log final status."""
        elapsed = time.time() - self.start_time
        rate = self.completed_items / elapsed if elapsed > 0 else 0
        
        status = "✅ COMPLETED" if success else "❌ FAILED"
        final_message = f"{status}: {self.name} - {self.completed_items}/{self.total_items} items in {elapsed/60:.1f}min ({rate:.1f} items/sec)"
        
        if message:
            final_message += f" - {message}"
        
        progress_logger.info(final_message)


@contextmanager
def track_progress(name: str, total_items: int):
    """Context manager for simple progress tracking."""
    progress = SimpleProgress(name, total_items)
    try:
        yield progress
        progress.complete(success=True)
    except Exception as e:
        progress.complete(success=False, message=str(e))
        raise


def log_phase(phase_name: str):
    """Log the start of a major phase."""
    progress_logger.info(f"🚀 PHASE: {phase_name}")


def log_step(step_name: str, details: str = ""):
    """Log a step within a phase."""
    message = f"   → {step_name}"
    if details:
        message += f": {details}"
    progress_logger.info(message)


def log_stats(stats: Dict[str, Any]):
    """Log statistics in a readable format."""
    progress_logger.info("📊 STATISTICS:")
    for key, value in stats.items():
        progress_logger.info(f"   {key}: {value}")


def log_error(error_msg: str, context: str = ""):
    """Log an error with context."""
    message = f"❌ ERROR: {error_msg}"
    if context:
        message += f" (Context: {context})"
    progress_logger.error(message)


def log_warning(warning_msg: str, context: str = ""):
    """Log a warning with context."""
    message = f"⚠️  WARNING: {warning_msg}"
    if context:
        message += f" (Context: {context})"
    progress_logger.warning(message)


def log_success(success_msg: str):
    """Log a success message."""
    progress_logger.info(f"✅ SUCCESS: {success_msg}")


# Example usage:
if __name__ == "__main__":
    # Example of how this would be used in the data extraction
    
    log_phase("Data Extraction")
    
    # Simple progress tracking
    with track_progress("Scraping team data", 32) as progress:
        for i in range(32):
            time.sleep(0.1)  # Simulate work
            progress.update()
    
    log_step("Processing snapcount data", "Football Guys scraper")
    
    # Manual progress for more control
    manual_progress = SimpleProgress("Processing game logs", 100)
    for i in range(100):
        time.sleep(0.01)  # Simulate work
        manual_progress.update()
    manual_progress.complete()
    
    log_stats({
        "Total players processed": 1500,
        "Total games": 272,
        "Cache hit rate": "85%",
        "Processing time": "12.5 minutes"
    })
    
    log_success("Data extraction completed successfully") 