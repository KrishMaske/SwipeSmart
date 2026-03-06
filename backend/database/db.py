from fastapi.params import Depends
from config.security import get_user_context
from utils.crypt import encrypt

def create_simplefin_connection(context, access_url):
    encrypted_url = encrypt(access_url)
    sb = context["supabase"]
    user_id = context["user_id"]

    response = (sb
                .table("simplefin_connections")
                .insert({"user_id": user_id, "access_url": encrypted_url})
                .execute())
    
    if response.status_code == 201:
        return {"success": "Connection created successfully"}
    else:
        return {"error": f"Failed to create connection: {response.status_code} - {response.text}"}