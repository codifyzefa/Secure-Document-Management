from __future__ import annotations

from database.repositories.counter_repository import CounterRepository
from logger.logging_config import get_logger

logger = get_logger(__name__)

DOCUMENT_ID_PREFIX: str = "DOC"
COUNTER_NAME: str = "document_id"
SEQUENCE_PADDING: int = 4


class DocumentIDService:
    """Generates human-readable, sequential Document IDs.

    Format: ``DOC-`` followed by a zero-padded sequence number
    (e.g. ``DOC-0001``, ``DOC-0002``, …).

    The service delegates counter management to
    :class:`~database.repositories.counter_repository.CounterRepository`
    so that sequence increments are atomic in MongoDB.
    """

    def __init__(self) -> None:
        self._counter_repo: CounterRepository = CounterRepository()

    def generate_document_id(self) -> str:
        """Return the next available Document ID in ``DOC-XXXX`` format.

        Returns:
            A unique sequential document identifier, e.g. ``DOC-0042``.

        Raises:
            CounterError: If the underlying MongoDB counter operation
                fails (wraps ``PyMongoError``).
        """
        seq: int = self._counter_repo.get_next_sequence(COUNTER_NAME)
        return f"{DOCUMENT_ID_PREFIX}-{seq:0{SEQUENCE_PADDING}d}"
