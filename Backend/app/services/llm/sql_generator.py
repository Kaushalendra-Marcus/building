import logging
from typing import Dict, Any

from app.services.llm.groq_service import generate_response
from app.middlewares.sql_sanitizer import sanitize_sql
logger = logging.getLogger(__name__)

DATABASE_SCHEMA = """
Tables:
sales
- id
- date
- revenue
- region
- product

customers
- id
- name
- city
- created_at

orders
- id
- customer_id
- amount
- status
- created_at
"""