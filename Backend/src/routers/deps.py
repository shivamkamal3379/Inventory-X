"""Shared router dependencies."""

from fastapi import Depends, Query

from src.core.config import settings
from src.core.security import get_current_user
from src.models.auth import User

# Applied at include_router level to every business router. Attaching it there
# rather than per-endpoint means a newly added route is protected by default —
# the previous code left every CRUD endpoint completely unauthenticated.
CurrentUser = Depends(get_current_user)


class Pagination:
    """skip/limit with a server-enforced ceiling, so a client cannot request
    the entire table in one call."""

    def __init__(
        self,
        skip: int = Query(default=0, ge=0),
        limit: int = Query(default=50, ge=1),
    ) -> None:
        self.skip = skip
        self.limit = min(limit, settings.MAX_PAGE_SIZE)


__all__ = ["CurrentUser", "Pagination", "User"]
