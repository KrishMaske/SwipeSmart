import os
import supabase
from cryptography.fernet import Fernet

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
jwks_url = os.getenv("SUPABASE_JWK")


fernet = Fernet(os.getenv("FERNET_KEY"))
