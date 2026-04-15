from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from ...domain.services import AccessTokenService
from .db_dependencies import get_jwt_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    jwt_service: AccessTokenService = Depends(get_jwt_service),
) -> dict:
    payload = jwt_service.verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload
