from fastapi import Depends, APIRouter
from typing import Optional

from ..depends import get_hospital_service, HospitalService
from ..dto.outbound import HospitalInfoResponse


router_hospital = APIRouter(prefix="/api/v1/hospital", tags=["医院"])


@router_hospital.get(
    "/hospital_info",
    summary="获取医院信息",
    response_model=Optional[HospitalInfoResponse],
)
async def get_hospital_info(
    hospital_service: HospitalService = Depends(get_hospital_service),
):
    result = await hospital_service.get_hospital_info(id=1)
    if result:
        return HospitalInfoResponse.model_validate(result)
    return None
