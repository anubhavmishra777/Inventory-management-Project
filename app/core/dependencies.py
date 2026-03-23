from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import verify_token
from app.modules.auth import service
from app.database.base import get_db
from sqlalchemy.orm import Session

# HTTPBearer returns HTTPAuthorizationCredentials object
oauth2_scheme = HTTPBearer()

async def get_current_user(token: HTTPAuthorizationCredentials = Depends(oauth2_scheme),db:Session=Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Extract the actual token string
    token_str = token.credentials

    # Verify token (assumed to return username or None)
    username = verify_token(token_str)
    if username is None:
        raise credentials_exception
    
    user = service.get_user_by_username(db,username)
    if user is None:
        raise credentials_exception

    return user

async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    if not current_user.get("is_active", True):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
