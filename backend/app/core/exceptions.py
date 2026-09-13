class NotFoundError(Exception):
    """Raised when an entity does not exist."""


class ModelNotReadyError(Exception):
    """Raised when an ML model is not trained or cannot be loaded."""

