from fastapi import APIRouter, Request, Query
from datetime import datetime
from utils.plaid_service import get_transactions
from database.queries import (sync_transactions_db)
from utils.auth_service import get_user_id

router = APIRouter()

@router.post("/api/transactions/sync/")
def sync_db(request: Request):
    user_id = get_user_id(request)

    items = get_transactions(user_id)

    total_added = total_modified = total_removed = 0
    total_processed = total_errors = 0

    for item in items:
        total_added += len(item.get("added", []) or [])
        total_modified += len(item.get("modified", []) or [])
        total_removed += len(item.get("removed", []) or [])

        db_result = sync_transactions_db(item, user_id, item["plaid_item_id"])
        total_processed += db_result.get("processed", 0)
        total_errors += db_result.get("errors", 0)

    return {
        "status": "ok",
        "plaid": {
            "added": total_added,
            "modified": total_modified,
            "removed": total_removed,
        },
        "db": {
            "status": "success",
            "processed": total_processed,
            "errors": total_errors,
        },
    }