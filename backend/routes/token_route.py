from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.item_get_request import ItemGetRequest
from plaid.model.institutions_get_by_id_request import InstitutionsGetByIdRequest

from config.settings import plaid_client, products, PLAID_REDIRECT_URI, PLAID_PRODUCTS
from utils.auth_service import get_user_id
from database.queries import upsert_bank_connection
from config.crypto import encrypt_access_token

router = APIRouter()

class PublicTokenPayload(BaseModel):
    public_token: str

@router.post("/api/create_link_token", tags=["link_token"])
async def create_link_token(request: Request):
    """
    Create a Plaid Link token tied to the authenticated user.
    """
    user_id = get_user_id(request)

    try:
        link_request = LinkTokenCreateRequest(
            products=products,
            client_name="SwipeSmart",
            country_codes=[CountryCode("US")],
            language="en",
            user=LinkTokenCreateRequestUser(
                client_user_id=user_id
            ),
        )

        if PLAID_REDIRECT_URI is not None:
            link_request.redirect_uri = PLAID_REDIRECT_URI

        response = plaid_client.link_token_create(link_request)
        return response.to_dict()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/exchange_public_token", tags=["access_token"])
async def exchange_public_token(request: Request, payload: PublicTokenPayload):
    user_id = get_user_id(request)

    try:
        public_token = payload.public_token

        exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        exchange_response = plaid_client.item_public_token_exchange(exchange_request).to_dict()

        access_token = exchange_response["access_token"]
        plaid_item_id = exchange_response["item_id"]

        # institution_id from item/get
        item_resp = plaid_client.item_get(ItemGetRequest(access_token=access_token)).to_dict()
        institution_id = item_resp.get("item", {}).get("institution_id")

        institution_name = None
        if institution_id:
            inst_resp = plaid_client.institutions_get_by_id(
                InstitutionsGetByIdRequest(
                    institution_id=institution_id,
                    country_codes=[CountryCode("US")]
                )
            ).to_dict()
            institution_name = inst_resp.get("institution", {}).get("name")

        access_token_enc = encrypt_access_token(access_token)

        upsert_bank_connection(
            user_id=user_id,
            plaid_item_id=plaid_item_id,
            access_token_enc=access_token_enc,
            institution_id=institution_id,
            institution_name=institution_name,
        )

        # never return access_token
        return {
            "status": "ok",
            "plaid_item_id": plaid_item_id,
            "institution_id": institution_id,
            "institution_name": institution_name,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))