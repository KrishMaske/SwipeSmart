from config.settings import supabase, supabase_admin


def get_access_token(user_id):
    try:
        if not user_id:
            raise ValueError("User ID is required to fetch access token.")
        response = supabase.table('bank_connections').select('access_token').eq('user_id', user_id).single().execute()
        data = response.data
        if data and 'access_token' in data:
            return data['access_token']
        else:
            raise ValueError("Access token not found for the given user ID.")
    except Exception as e:
        print(f"Error fetching access token for user {user_id}: {e}")
        return None

def sync_transactions_db(sync_result, user_id: str, plaid_item_id: str):
    added = sync_result.get("added", []) or []
    modified = sync_result.get("modified", []) or []
    removed = sync_result.get("removed", []) or []

    success = 0
    error = 0

    for transaction in (added + modified)[::-1]:
        try:
            pfc = transaction.get("personal_finance_category")

            supabase_admin.table("transactions").upsert({
                "user_id": user_id,
                "plaid_item_id": plaid_item_id,
                "plaid_transaction_id": transaction.get("transaction_id"),
                "plaid_account_id": transaction.get("account_id"),
                "name": transaction.get("merchant_name") or transaction.get("name"),
                "amount": transaction.get("amount"),
                "date": (
                    transaction.get("date").isoformat()
                    if hasattr(transaction.get("date"), "isoformat")
                    else transaction.get("date")
                ),
                "category": pfc.get("primary") if pfc else None,
                "detailed_category": pfc.get("detailed") if pfc else None,
            }, on_conflict="plaid_item_id,plaid_transaction_id").execute()

            success += 1
        except Exception as e:
            print(f"Error upserting transaction {transaction.get('transaction_id')}: {e}")
            error += 1

    for r in removed:
        try:
            tx_id = r.get("transaction_id")
            if not tx_id:
                continue

            supabase_admin.table("transactions") \
                .delete() \
                .eq("user_id", user_id) \
                .eq("plaid_item_id", plaid_item_id) \
                .eq("plaid_transaction_id", tx_id) \
                .execute()
        except Exception as e:
            print(f"Error deleting removed transaction {r.get('transaction_id')}: {e}")
            error += 1

    return {"status": "success", "processed": success, "errors": error}



def upsert_bank_connection(user_id, plaid_item_id, access_token_enc, institution_id=None, institution_name=None):
    resp = (
        supabase_admin
        .table("bank_connections")
        .upsert({
            "user_id": user_id,
            "plaid_item_id": plaid_item_id,
            "access_token_enc": access_token_enc,
            "institution_id": institution_id,
            "institution_name": institution_name,
        }, on_conflict="user_id,plaid_item_id")
        .execute()
    )
    return resp.data


def get_bank_connections(user_id: str):
    """
    Fetch all Plaid Items (bank connections) for a user.
    """
    if not user_id:
        raise ValueError("user_id is required")
    
    resp = (
        supabase_admin
        .table("bank_connections")
        .select("plaid_item_id, access_token_enc, institution_id, institution_name")
        .eq("user_id", user_id)
        .execute()
    )
    return resp.data or []

def get_transactions_cursor(user_id: str, plaid_item_id: str) -> str | None:
    resp = (
        supabase_admin
        .table("bank_connections")
        .select("transactions_cursor")
        .eq("user_id", user_id)
        .eq("plaid_item_id", plaid_item_id)
        .maybe_single()
        .execute()
    )
    data = resp.data
    return data.get("transactions_cursor") if data else None

def update_transactions_cursor(user_id: str, plaid_item_id: str, cursor: str):
    (
        supabase_admin
        .table("bank_connections")
        .update({"transactions_cursor": cursor})
        .eq("user_id", user_id)
        .eq("plaid_item_id", plaid_item_id)
        .execute()
    )