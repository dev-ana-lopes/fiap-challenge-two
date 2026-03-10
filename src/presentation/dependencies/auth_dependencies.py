from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from ...infrastructure.config.settings import Settings, get_settings
from ...infrastructure.email.jwt_service import JwtService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    settings: Settings = Depends(get_settings),
) -> dict:
    jwt_service = JwtService(settings)
    payload = jwt_service.verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload
