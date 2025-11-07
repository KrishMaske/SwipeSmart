from config.settings import plaid_client
import plaid
from plaid.model.transactions_sync_request import TransactionsSyncRequest



def get_transactions(token):
    access_token = token['access_token']
    request = TransactionsSyncRequest(
        access_token=access_token,
    )
    response = plaid_client.transactions_sync(request)
    transactions = response['added'] or []

    # the transactions in the response are paginated, so make multiple calls while incrementing the cursor to
    # retrieve all transactions
    while (response['has_more']):
        request = TransactionsSyncRequest(
            access_token=access_token,
            cursor=response['next_cursor']
        )
        response = plaid_client.transactions_sync(request)
        transactions += response['added'] or []
    
    return transactions