from datetime import date, datetime


from ..repo import DoctorRepository


class DoctorService:

    def __init__(self, doctor_repo: DoctorRepository):
        self.doctor_repo = doctor_repo

    async def get_doctor_list_infos(self, enable: int = 1):
        results = await self.doctor_repo.get_doctor_list_infos(enable)
        for result in results:
            print(result)
        return results

    async def get_available_doctor(self, dno, enable: int = 1):
        return await self.doctor_repo.get_available_doctor(dno, enable)

    async def get_doctor_scheduling_info(self, dno, dt: str, enable: int = 1):

        if not dt:
            dt = datetime.now().date()
        else:
            dt = datetime.strptime(dt, "%Y-%m-%d").date()

        doctor, doctor_scheduling_result = await self.doctor_repo.get_doctor_scheduling_info(dno, dt, enable)
        print(doctor, doctor_scheduling_result)
        

        ams = []
        pms = []

        for s in doctor_scheduling_result:
            if s.ampm == "am":
                ams.append(s)
            else:
                pms.append(s)

        result = {}
        result["doctor"] = doctor
        result["scheduling_info"] = {
            "am": ams,
            "pm": pms
        }
        print(result)
        return result
            


