import os
import uuid


def sanitize_filename(filename: str) -> str:
    """Reduce a client-supplied filename to a safe basename.

    Strips directory components (including Windows-style separators) so the
    value can be joined onto a directory without escaping it, and falls back
    to a generated name when nothing safe remains.
    """
    name = os.path.basename((filename or "").replace("\\", "/"))
    if name in ("", ".", ".."):
        return str(uuid.uuid1())
    return name
