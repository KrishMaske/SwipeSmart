from config.settings import plaid_client
from datetime import date, timedelta

from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions

from database.queries import (
    get_bank_connections,
    get_transactions_cursor,
    update_transactions_cursor,
)
from config.crypto import decrypt_access_token  # <-- replace with your actual import


def backfill_transactions_for_access_token(access_token: str, days: int = 365):
    start_date = date.today() - timedelta(days=days)
    end_date = date.today()

    all_tx = []
    offset = 0
    count = 100

    while True:
        req = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date,
            options=TransactionsGetRequestOptions(count=count, offset=offset),
        )
        resp = plaid_client.transactions_get(req).to_dict()
        print("TOTAL:", resp.get("total_transactions"))

        txs = resp.get("transactions", []) or []
        all_tx += txs

        total = resp.get("total_transactions", 0)
        offset += len(txs)

        if offset >= total or len(txs) == 0:
            break

    return all_tx

def sync_transactions_for_access_token(access_token: str, cursor: str | None):
    """
    Syncs ONE Plaid Item via /transactions/sync and returns:
    added, modified, removed, next_cursor
    """
    print("Syncing transactions with cursor:")
    added, modified, removed = [], [], []
    next_cursor = cursor
    has_more = True
    
    while has_more:
        if next_cursor:
            req = TransactionsSyncRequest(access_token=access_token, cursor=next_cursor)
        else:
            req = TransactionsSyncRequest(access_token=access_token)

        resp = plaid_client.transactions_sync(req).to_dict()

        added += resp.get("added", []) or []
        modified += resp.get("modified", []) or []
        removed += resp.get("removed", []) or []

        has_more = resp.get("has_more", False)
        next_cursor = resp.get("next_cursor")
        
    return {
        "added": added,
        "modified": modified,
        "removed": removed,
        "next_cursor": next_cursor,
    }


def get_transactions(user_id: str):
    conns = get_bank_connections(user_id)
    results = []

    for conn in conns:
        plaid_item_id = conn["plaid_item_id"]
        access_token = decrypt_access_token(conn["access_token_enc"])
        cursor = get_transactions_cursor(user_id, plaid_item_id)

        added, modified, removed = [], [], []

        if cursor is None:
            history = backfill_transactions_for_access_token(access_token, days=365)
            added += history

        result = sync_transactions_for_access_token(access_token, cursor)

        if result["next_cursor"]:
            update_transactions_cursor(user_id, plaid_item_id, result["next_cursor"])

        added += result["added"]
        modified += result["modified"]
        removed += result["removed"]

        results.append({
            "plaid_item_id": plaid_item_id,
            "added": added,
            "modified": modified,
            "removed": removed,
        })

    return results