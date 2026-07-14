from __future__ import annotations

from typing import Any

from pymongo.collection import ReturnDocument
from pymongo.errors import PyMongoError

from database.exceptions import CounterError
from database.manager import DatabaseManager
from exceptions.custom_exceptions import DatabaseError
from logger.logging_config import get_logger

logger = get_logger(__name__)


class CounterRepository:
    """Manages atomic sequence counters in MongoDB.

    Uses ``find_one_and_update`` with ``$inc`` to guarantee
    uniqueness even under concurrent uploads.
    """

    _collection_name: str = "counters"

    def __init__(self) -> None:
        self._db_mgr: DatabaseManager = DatabaseManager()

    @property
    def _collection(self):
        return self._db_mgr.get_collection(self._collection_name)

    def get_next_sequence(self, counter_name: str) -> int:
        """Atomically increment the named counter and return the new value.

        If the counter does not exist it is initialised at 1.
        """
        try:
            result: dict[str, Any] | None = self._collection.find_one_and_update(
                {"_id": counter_name},
                {"$inc": {"sequence_value": 1}},
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )
            return result["sequence_value"]
        except PyMongoError as exc:
            raise CounterError(
                f"Failed to get next sequence for '{counter_name}': {exc}"
            ) from exc

    def get_current_sequence(self, counter_name: str) -> int:
        """Return the current value of a counter (non-destructive).

        Returns 0 if the counter has never been used.
        """
        try:
            doc: dict[str, Any] | None = self._collection.find_one(
                {"_id": counter_name}
            )
            if doc is None:
                return 0
            return doc.get("sequence_value", 0)
        except PyMongoError as exc:
            raise CounterError(
                f"Failed to get current sequence for '{counter_name}': {exc}"
            ) from exc

    def reset_counter(self, counter_name: str) -> None:
        """Reset a counter to zero (useful only for testing)."""
        try:
            self._collection.update_one(
                {"_id": counter_name},
                {"$set": {"sequence_value": 0}},
                upsert=True,
            )
        except PyMongoError as exc:
            raise CounterError(
                f"Failed to reset counter '{counter_name}': {exc}"
            ) from exc
