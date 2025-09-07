

from ..repo.hospital import HospitalRepository

class HospitalService:

    def __init__(self, hospital_repo: HospitalRepository):
        self.hospital_repo = hospital_repo

    async def get_hospital_info(self, id: int):
        return await self.hospital_repo.get_hospital_info(id)