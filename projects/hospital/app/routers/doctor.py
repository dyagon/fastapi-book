from fastapi import APIRouter, Depends
from fastapi import Query

from datetime import datetime, date
from ..depends import get_doctor_service
from ..dto.outbound import DoctorListResponse, DoctorInfoResponse, DoctorSchedulingInfoResponse

from ..depends import DoctorService, get_doctor_service

router_doctor = APIRouter(prefix="/api/v1/doctor", tags=["医生"])


@router_doctor.get(
    "/doctor_list", summary="获取医生列表", response_model=DoctorListResponse
)
async def get_doctor_list(doctor_service: DoctorService = Depends(get_doctor_service)):
    result = await doctor_service.get_doctor_list_infos()
    return DoctorListResponse(
        doctor_list=[DoctorInfoResponse.model_validate(doctor) for doctor in result]
    )


@router_doctor.get("/doctor_scheduling_info", summary="获取医生排班信息")
async def get_doctor_scheduling_info(
    dt: str = Query(..., description="查询日期"),
    dno: str = Query(..., description="医生编号"),
    doctor_service: DoctorService = Depends(get_doctor_service),
):
    result = await doctor_service.get_doctor_scheduling_info(dno, dt)
    return DoctorSchedulingInfoResponse.model_validate(result)