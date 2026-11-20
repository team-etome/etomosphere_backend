def success_(code: int = 1001, message: str = "Success", data=None):
    return {
        "status": code,
        "message": message,
        "data": data if data is not None else {}
    }

def error_(code: int = -1, message="error", data=None):
    return {
        "status": code,
        "message": message,
        "data": data if data is not None else {}
    }