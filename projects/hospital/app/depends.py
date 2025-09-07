from typing import AsyncGenerator

from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from ..infra import SessionLocal

from ..domain.repo import HospitalRepository, DoctorRepository
from ..domain.service import HospitalService, DoctorService


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    db_session = None
    try:
        db_session = SessionLocal()
        yield db_session
        await db_session.commit()
    except SQLAlchemyError as ex:
        await db_session.rollback()
        raise ex
    finally:
        await db_session.close()



async def get_hospital_repo(db: AsyncSession = Depends(get_db_session)):
    yield HospitalRepository(db)


async def get_hospital_service(hospital_repo: HospitalRepository = Depends(get_hospital_repo)):
    yield HospitalService(hospital_repo)


async def get_doctor_repo(db: AsyncSession = Depends(get_db_session)):
    yield DoctorRepository(db)

async def get_doctor_service(doctor_repo: DoctorRepository = Depends(get_doctor_repo)):
    yield DoctorService(doctor_repo)

