STATUS_MAP = {
    "SUCCESS": {
        "status_code": 200,
        "message": "OK",
    },
    "NO_CONTENT": {
        "status_code": 204,
        "message": "No content to return for this request",
    },
    "BAD_REQUEST": {
        "status_code": 400,
        "message": "Warning: Validation failed. Required values not found",
    },
    "UNAUTHORIZED": {
        "status_code": 401,
        "message": "Unauthorized: Invalid Internal API Key",
    },
    "METHOD_NOT_ALLOWED": {
        "status_code": 405,
        "message": "Error: Method not allowed",
    },
    "INTERNAL_SERVER_ERROR": {
        "status_code": 500,
        "message": "Error: An unexpected error occurred. Please try again later",
    },
    "PARSE_ERROR": {
        "status_code": 500,
        "message": "Error: Failed to parse model response JSON",
    },
}
