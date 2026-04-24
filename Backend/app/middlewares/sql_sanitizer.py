import re
from fastapi import HTTPException, status

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


def sanitize_sql(query: str) -> str:
    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty query",
        )

    if len(query) > MAX_QUERY_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Query too long"
        )
    cleaned_query = query.strip().upper()

    if ";" in cleaned_query:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Multiple statements not allowed",
        )

    if "--" in cleaned_query or "/*" in cleaned_query:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="SQL comments not allowed"
        )

    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{keyword}\b", cleaned_query):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden SQL operation: {keyword}",
            )

    if not any(cleaned_query.startswith(k) for k in ALLOWED_START):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only SELECT queries are allowed",
        )

    return query
