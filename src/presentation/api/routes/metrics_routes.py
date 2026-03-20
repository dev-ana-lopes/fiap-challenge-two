from typing import Annotated

from fastapi import APIRouter, Depends

from ....application.use_cases.metrics_use_case import GetAverageExecutionTimeUseCase
from ....presentation.dependencies.auth_dependencies import get_current_user
from ....presentation.dependencies.db_dependencies import get_service_order_repository
from ....presentation.schemas.admin_schema import AverageExecutionTimeResponse

router = APIRouter(
    prefix="/metrics",
    tags=["metrics"],
    dependencies=[Depends(get_current_user)],
)

ServiceOrderRepo = Annotated[object, Depends(get_service_order_repository)]


@router.get("/average-execution-time")
async def get_average_execution_time(
    service_order_repo: ServiceOrderRepo,
) -> AverageExecutionTimeResponse:
    use_case = GetAverageExecutionTimeUseCase(service_order_repo)
    avg = await use_case.execute()
    return AverageExecutionTimeResponse(average_execution_time_seconds=avg)
