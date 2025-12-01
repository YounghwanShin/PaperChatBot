"""Simple in-memory task status store for background tasks."""

from typing import Dict, Any, Optional
from threading import Lock
import uuid


class TaskStore:
    """Thread-safe in-memory task status store."""

    def __init__(self):
        """Initialize the task store."""
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()

    def create_task(self) -> str:
        """Create a new task and return its ID.

        Returns:
            Task ID
        """
        task_id = str(uuid.uuid4())
        with self._lock:
            self._tasks[task_id] = {
                "status": "processing",
                "progress": "Starting arXiv fetch...",
                "result": None,
                "error": None
            }
        return task_id

    def update_progress(self, task_id: str, progress: str) -> None:
        """Update task progress message.

        Args:
            task_id: Task identifier
            progress: Progress message
        """
        with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id]["progress"] = progress

    def set_completed(self, task_id: str, result: Dict[str, Any]) -> None:
        """Mark task as completed with result.

        Args:
            task_id: Task identifier
            result: Task result
        """
        with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id]["status"] = "completed"
                self._tasks[task_id]["result"] = result
                self._tasks[task_id]["progress"] = "Completed"

    def set_failed(self, task_id: str, error: str) -> None:
        """Mark task as failed with error message.

        Args:
            task_id: Task identifier
            error: Error message
        """
        with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id]["status"] = "failed"
                self._tasks[task_id]["error"] = error
                self._tasks[task_id]["progress"] = "Failed"

    def get_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status.

        Args:
            task_id: Task identifier

        Returns:
            Task status dict or None if not found
        """
        with self._lock:
            return self._tasks.get(task_id)

    def cleanup_task(self, task_id: str) -> None:
        """Remove task from store.

        Args:
            task_id: Task identifier
        """
        with self._lock:
            self._tasks.pop(task_id, None)


# Global task store instance
task_store = TaskStore()
