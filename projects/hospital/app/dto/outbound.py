from pydantic import BaseModel
from typing import Optional

from datetime import date, datetime

class HospitalInfoResponse(BaseModel):
    """医院信息响应模型"""

    name: str
    describe: str
    describeimages: str

    model_config = {"from_attributes": True}


class DoctorInfoResponse(BaseModel):
    """医生信息响应模型"""

    dno: str
    dnname: str
    fee: float
    pic: str
    rank: str

    model_config = {"from_attributes": True}


class DoctorListResponse(BaseModel):
    """医生列表响应模型"""

    doctor_list: list[DoctorInfoResponse]


class ScheduleInfoResponse(BaseModel):
    """排班信息响应模型"""
    nsindex: str
    ampm: str
    dnotime: date
    nsnum: int
    nsnumstock: int
    tiempm: datetime
    tiemampmstr: str

    model_config = {"from_attributes": True}


class ScheduleInfoListResponse(BaseModel):
    
    am: list[ScheduleInfoResponse]
    pm: list[ScheduleInfoResponse]

    model_config = {"from_attributes": True}


class DoctorSchedulingInfoResponse(BaseModel):
    """医生排班信息响应模型"""

    doctor: DoctorInfoResponse
    scheduling_info: ScheduleInfoListResponse

    model_config = {"from_attributes": True}


class SchedulingInfo(BaseModel):
    # 预约医生编号
    dno: str
    # 预约时间
    start_time: str | None = None
