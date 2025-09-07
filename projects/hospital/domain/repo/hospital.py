from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models import Hospitalinfo


class HospitalRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_hospital_info(self, id: int):
        _result = await self.db.execute(
            select(Hospitalinfo).where(Hospitalinfo.id == id)
        )
        return _result.scalars().first()
