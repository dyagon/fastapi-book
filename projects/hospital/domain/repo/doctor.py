from typing import Optional
from datetime import datetime, date

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from ...infra.utils.datetime_helper import DatetimeHelper

from ..models import Doctorinfo, DoctorScheduling, DoctorSubscribeinfo


class DoctorRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_doctor_list_infos(self, enable: int = 1):
        query = select(Doctorinfo).where(Doctorinfo.enable == enable)
        _result = await self.db.execute(query)
        return _result.scalars().all()

    async def get_available_doctor(self, dno, enable: int = 1):
        query = select(Doctorinfo).where(
            Doctorinfo.enable == enable, Doctorinfo.dno == dno
        )
        _result = await self.db.execute(query)
        return _result.scalars().first()

    async def get_doctor_scheduling_info(self, dno, dt: date = None, enable: int = 1):
        doctor = await self.get_available_doctor(dno)
        # 再查询当前医生下面分开上午 和下午的排班信息
        doctor_scheduling_result = []
        if doctor:
            query = select(DoctorScheduling).where(
                DoctorScheduling.enable == enable, DoctorScheduling.dno == dno
            )
            if dt:
                query = query.where(DoctorScheduling.dnotime == dt)
            else:
                query = query.where(DoctorScheduling.dnotime == datetime.now().date())
            _result = await self.db.execute(query)
            doctor_scheduling_result = _result.scalars().all()
        return doctor, doctor_scheduling_result

    async def get_doctor_curr_nsindex_scheduling_info(
        self, dno, nsindex, enable: int = 1
    ):
        query = select(
            Doctorinfo.dno,
            Doctorinfo.dnname,
            Doctorinfo.pic,
            Doctorinfo.rank,
            Doctorinfo.addr,
            Doctorinfo.fee,
        )
        _result = await self.db.execute(
            query.where(Doctorinfo.enable == enable, Doctorinfo.dno == dno)
        )
        doctor_result: Optional[Doctorinfo] = _result.first()
        # 再查询当前医生下面分开上午 和下午的排班信息
        doctor_nsnuminfo_result: Optional[DoctorScheduling] = None
        if doctor_result:
            query = select(
                DoctorScheduling.nsindex,
                DoctorScheduling.ampm,
                DoctorScheduling.dnotime,
                DoctorScheduling.nsnum,
                DoctorScheduling.nsnumstock,
                DoctorScheduling.tiempm,
                DoctorScheduling.tiemampmstr,
            )
            query = query.where(
                DoctorScheduling.enable == enable,
                DoctorScheduling.dno == dno,
                DoctorScheduling.nsindex == nsindex,
            )
            _result = await self.db.execute(query)
            doctor_nsnuminfo_result = _result.first()
        return doctor_result, doctor_nsnuminfo_result

    async def updata_nusnum_info_dno(self, dno, nsindex, isup=True):
        response = update(DoctorSubscribeinfo).where(
            DoctorScheduling.dno == dno, DoctorScheduling.nsindex == nsindex
        )
        if isup:
            result = await self.db.execute(
                response.values(use_nsnum=DoctorScheduling.use_nsnum + 1)
            )
        else:
            result = await self.db.execute(
                response.values(use_nsnum=DoctorScheduling.use_nsnum - 1)
            )
        await self.db.commit()
        return result.rowcount
