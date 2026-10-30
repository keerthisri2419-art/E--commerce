import os
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

# Load env variables from root folder
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
load_dotenv(dotenv_path)

security = HTTPBearer()
bypass_auth = os.getenv("BYPASS_AUTH", "true").lower() == "true"

# Define mock users corresponding to demo options in front-end
MOCK_USERS = {
    "demo-buyer": {
        "uid": "demo-buyer-uid",
        "email": "gnanavel@ecom.com",
        "name": "Gnanavel",
        "role": "buyer"
    },
    "demo-seller": {
        "uid": "demo-seller-uid",
        "email": "elena.thorne@terra.com",
        "name": "Elena Thorne",
        "role": "seller"
    }
}

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    
    # 1. Check if token is a demo token and bypass is enabled
    if bypass_auth and token in MOCK_USERS:
        return MOCK_USERS[token]
        
    # 2. Attempt real Firebase Auth validation
    try:
        from firebase_admin import auth
        decoded_token = auth.verify_id_token(token)
        # Infer role if not explicitly set (e.g. default to buyer or parse from claims)
        # You can add custom user claims dynamically, but let's default to role from email
        email = decoded_token.get("email", "")
        role = "seller" if "seller" in email or "thorne" in email else "buyer"
        decoded_token["role"] = decoded_token.get("role", role)
        decoded_token["name"] = decoded_token.get("name", decoded_token.get("email", "Conscious User"))
        return decoded_token
    except Exception as e:
        # If real verification fails, check if we can fall back to mock profiles for safety
        if bypass_auth:
            # Check if it looks like a demo role token
            if "seller" in token.lower():
                return MOCK_USERS["demo-seller"]
            return MOCK_USERS["demo-buyer"]
            
        raise HTTPException(
            status_code=401,
            detail=f"Invalid or expired credentials: {str(e)}"
        )

def require_seller(user: dict = Depends(get_current_user)):
    if user.get("role") != "seller":
        raise HTTPException(
            status_code=403,
            detail="Access forbidden: This action requires a Seller role."
        )
    return user

def require_buyer(user: dict = Depends(get_current_user)):
    if user.get("role") != "buyer":
        raise HTTPException(
            status_code=403,
            detail="Access forbidden: This action requires a Buyer role."
        )
    return user
