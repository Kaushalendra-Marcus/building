import re
import logging
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

FORBIDDEN_KEYWORDS = [
    "DROP",
    "DELETE",
    "UPDATE",
    "INSERT",
    "ALTER",
    "TRUNCATE",
    "EXEC",
    "MERGE",
]

ALLOWED_START = ["SELECT", "WITH"]
MAX_QUERY_LENGTH = 1000


def remove_strings(q: str):
    return re.sub(r"'[^']*'", "", q)


def sanitize_sql(query: str) -> str:
    if not query:
        raise HTTPException(status_code=400, detail="Empty query")

    if len(query) > MAX_QUERY_LENGTH:
        raise HTTPException(status_code=400, detail="Query too long")

    cleaned_query = query.strip().upper()

    scan_query = remove_strings(cleaned_query)

    if ";" in scan_query[:-1]:
        raise HTTPException(
            status_code=403,
            detail="Multiple statements not allowed",
        )

    if "--" in scan_query or "/*" in scan_query:
        raise HTTPException(
            status_code=403,
            detail="SQL comments not allowed",
        )

    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(rf"(?<!\w){keyword}(?!\w)", scan_query):
            logger.warning(f"Blocked dangerous query: {query}")
            raise HTTPException(
                status_code=403,
                detail=f"Forbidden SQL operation: {keyword}",
            )

    if not any(scan_query.startswith(k) for k in ALLOWED_START):
        raise HTTPException(
            status_code=403,
            detail="Only SELECT queries are allowed",
        )

    if "LIMIT" not in scan_query:
        raise HTTPException(
            status_code=403,
            detail="Query must include LIMIT",
        )

    return query
