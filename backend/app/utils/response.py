from typing import Any


def ok(data: Any = None, message: str = "ok") -> dict[str, Any]:
    return {"status": "success", "message": message, "data": data}

