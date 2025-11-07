from urllib3 import request
from fastapi import APIRouter, Request
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from config.settings import plaid_client, products, PLAID_REDIRECT_URI

router = APIRouter()

@router.post("api/public_token/create", tags=["public_token"])
async def create_link_token():
    try:
        request = LinkTokenCreateRequest(
            products=products,
            client_name="Plaid Quickstart",
            country_codes=CountryCode("US"),
            language="en",
                    user=LinkTokenCreateRequestUser(
                client_user_id="Plaid Quickstart"
            ),
        )
        if PLAID_REDIRECT_URI!=None:
            request['redirect_uri']=PLAID_REDIRECT_URI
        response = plaid_client.link_token_create(request)
        return {"data": response.to_dict()}
    except Exception as e:
        print(e)
        return {"error": str(e)}
    

@router.post("api/public_token/exchange", tags=["access_token"])
async def exchange_public_token(request: Request):
    body = await request.json()
    public_token = body['public_token']
    exchange_request = ItemPublicTokenExchangeRequest(
        public_token=public_token
    )
    exchange_response = plaid_client.item_public_token_exchange(exchange_request).to_dict()
    access_token = exchange_response['access_token']
    item_id = exchange_response['item_id']
    return {"access_token": access_token, "item_id": item_id}