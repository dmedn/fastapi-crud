from datetime import datetime, timezone
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column


def get_current_dt() -> datetime:
    dt = datetime.now(tz=timezone.utc)
    return dt.replace(microsecond=0, tzinfo=None)


class CreatedAtMixin:
    """
    Mixin that automatically stores the creation timestamp of a database record.

    This mixin defines a `created_at` field, which is automatically populated
    when the record is created, using the current UTC time. It ensures
    consistency across models by centralizing timestamp behavior.

    Fields:
        created_at — datetime indicating when the record was created.

    Notes:
        - The timestamp is stored without microseconds for cleaner formatting.
        - Uses a server-side default (`func.now()`) to ensure accurate database time.
        - Can be combined with other mixins such as `UpdatedAtMixin` if needed.
    """
    created_at: Mapped[datetime] = mapped_column(default=get_current_dt, server_default=func.now())
