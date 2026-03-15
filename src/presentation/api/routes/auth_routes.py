from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from ....application.dto.login_dto import LoginDTO
from ....application.use_cases.auth_use_case import (
    AuthenticateUserUseCase,
    RegisterUserUseCase,
)
from ....domain.repositories.user_repository import UserRepository
from ....infrastructure.email.jwt_service import JwtService
from ....infrastructure.email.password_hasher import PasswordHasher
from ....presentation.dependencies.db_dependencies import (
    get_jwt_service, get_password_hasher, get_user_repository)
from ....presentation.schemas.service_order_schema import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    password_hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
) -> RegisterResponse:
    existing = await user_repo.get_by_email(request.email)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    use_case = RegisterUserUseCase(user_repo, password_hasher)
    user_id = await use_case.execute(request.email, request.password)
    return RegisterResponse(user_id=user_id)


@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordBearer, Depends()],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    password_hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
    jwt_service: Annotated[JwtService, Depends(get_jwt_service)],
) -> LoginResponse:
    dto = LoginDTO(email=form_data.username, password=form_data.password)

    use_case = AuthenticateUserUseCase(user_repo, password_hasher, jwt_service)
    token = await use_case.execute(dto)

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    return LoginResponse(access_token=token)


@router.post("/login-json")
async def login_json(
    request: LoginRequest,
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    password_hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
    jwt_service: Annotated[JwtService, Depends(get_jwt_service)],
) -> LoginResponse:
    dto = LoginDTO(email=request.email, password=request.password)

    use_case = AuthenticateUserUseCase(user_repo, password_hasher, jwt_service)
    token = await use_case.execute(dto)

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    return LoginResponse(access_token=token)
