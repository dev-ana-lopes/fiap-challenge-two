from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ....application.use_cases.vehicle_use_cases import (
    CreateVehicleUseCase,
    DeleteVehicleUseCase,
    GetVehicleUseCase,
    ListVehiclesUseCase,
    UpdateVehicleUseCase,
)
from ....presentation.dependencies.auth_dependencies import get_current_user
from ....presentation.dependencies.db_dependencies import (
    get_customer_repository,
    get_vehicle_repository,
)
from ....presentation.schemas.admin_schema import (
    VehicleCreateRequest,
    VehicleResponse,
    VehicleUpdateRequest,
)

router = APIRouter(
    prefix="/vehicles",
    tags=["vehicles"],
    dependencies=[Depends(get_current_user)],
)

VehicleRepo = Annotated[object, Depends(get_vehicle_repository)]
CustomerRepo = Annotated[object, Depends(get_customer_repository)]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_vehicle(
    request: VehicleCreateRequest,
    vehicle_repo: VehicleRepo,
    customer_repo: CustomerRepo,
) -> dict:
    use_case = CreateVehicleUseCase(vehicle_repo, customer_repo)
    try:
        vehicle_id = await use_case.execute(
            UUID(request.customer_id),
            request.brand,
            request.model,
            request.year,
            request.plate,
        )
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    return {"vehicle_id": vehicle_id}


@router.get("")
async def list_vehicles(
    vehicle_repo: VehicleRepo,
    customer_id: str | None = Query(default=None),
) -> list[VehicleResponse]:
    use_case = ListVehiclesUseCase(vehicle_repo)
    vehicles = await use_case.execute(UUID(customer_id) if customer_id else None)
    return [
        VehicleResponse(
            id=str(v.id),
            customer_id=str(v.customer_id),
            brand=v.brand,
            model=v.model,
            year=v.year,
            plate=v.plate,
        )
        for v in vehicles
    ]


@router.get("/{vehicle_id}")
async def get_vehicle(vehicle_id: UUID, vehicle_repo: VehicleRepo) -> VehicleResponse:
    use_case = GetVehicleUseCase(vehicle_repo)
    vehicle = await use_case.execute(vehicle_id)
    if vehicle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return VehicleResponse(
        id=str(vehicle.id),
        customer_id=str(vehicle.customer_id),
        brand=vehicle.brand,
        model=vehicle.model,
        year=vehicle.year,
        plate=vehicle.plate,
    )


@router.put("/{vehicle_id}")
async def update_vehicle(
    vehicle_id: UUID,
    request: VehicleUpdateRequest,
    vehicle_repo: VehicleRepo,
    customer_repo: CustomerRepo,
) -> dict:
    use_case = UpdateVehicleUseCase(vehicle_repo, customer_repo)
    try:
        ok = await use_case.execute(
            vehicle_id,
            UUID(request.customer_id),
            request.brand,
            request.model,
            request.year,
            request.plate,
        )
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return {"success": True}


@router.delete("/{vehicle_id}")
async def delete_vehicle(vehicle_id: UUID, vehicle_repo: VehicleRepo) -> dict:
    use_case = DeleteVehicleUseCase(vehicle_repo)
    ok = await use_case.execute(vehicle_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return {"success": True}
