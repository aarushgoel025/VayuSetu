from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from config import SUPABASE_JWT_SECRET
from db import supabase

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    FastAPI dependency that extracts the Bearer token, decodes and verifies it
    using the Supabase JWT Secret. It also dynamically attaches the user JWT
    to the Supabase client context to enforce Row-Level Security (RLS).
    """
    token = credentials.credentials
    
    # 1. If JWT Secret is configured, decode locally (fastest, 0ms latency)
    if SUPABASE_JWT_SECRET:
        try:
            payload = jwt.decode(
                token,
                SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                audience="authenticated"
            )
            # Inject user context dynamically into Supabase client for RLS checks
            if supabase:
                supabase.postgrest.auth(token)
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid authentication credentials: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Authentication error: {str(e)}"
            )
            
    # 2. Fallback to Supabase API validation if secret is not set (e.g., local dev bootstrap)
    else:
        if not supabase:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Supabase client not initialized and SUPABASE_JWT_SECRET is missing."
            )
        try:
            # Query the Supabase Auth server directly using the token
            user_resp = supabase.auth.get_user(token)
            user_data = user_resp.user
            
            # Map into a standard payload structure
            payload = {
                "sub": user_data.id,
                "email": user_data.email,
                "user_metadata": user_data.user_metadata or {},
                "app_metadata": user_data.app_metadata or {}
            }
            
            # Inject user context dynamically
            supabase.postgrest.auth(token)
            return payload
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Session validation failed: {str(e)}"
            )

def require_authority_write(user: dict = Depends(get_current_user)) -> dict:
    """
    FastAPI dependency that builds on top of get_current_user to check if the
    authenticated user has authority write/action permissions.
    Checks user_metadata or app_metadata for 'officer', 'admin', or 'authority' role.
    """
    user_metadata = user.get("user_metadata", {}) or {}
    app_metadata = user.get("app_metadata", {}) or {}
    
    # We inspect both app_metadata and user_metadata for role claims
    role = user_metadata.get("role") or app_metadata.get("role")
    
    allowed_roles = ["officer", "admin", "authority"]
    if role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation forbidden: Authority write permissions required"
        )
        
    return user
