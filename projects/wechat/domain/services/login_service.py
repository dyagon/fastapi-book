
from ..models.session import QRSession, UserInfo
from ..repos.session_repo import SessionRepository
from ..exceptions import WeChatAPIException
from typing import Optional
import random
import string


class WechatLoginService:

    def __init__(self, session_repo: SessionRepository):
        self.session_repo = session_repo

    async def create_qr_session(self, app_id: str, redirect_uri: str, state_param: str):
        session = QRSession(
            app_id=app_id,
            redirect_uri=redirect_uri,
            state=state_param
        )
        return await self.session_repo.create_session(session)
    
    async def get_session(self, session_id: str) -> Optional[QRSession]:
        """获取会话"""
        return await self.session_repo.get_session(session_id)

    async def mark_scanned(self, session_id: str, user_info: UserInfo) -> Optional[QRSession]:
        """标记会话为已扫描"""
        return await self.session_repo.mark_scanned(session_id, user_info)
    
    async def mark_confirmed(self, session_id: str, code: str = None) -> Optional[QRSession]:
        """标记会话为已确认"""
        if code is None:
            # 生成随机的一次性code
            code = "".join(random.choices(string.ascii_letters + string.digits, k=16))
        return await self.session_repo.mark_confirmed(session_id, code)
    
    async def mark_cancelled(self, session_id: str) -> Optional[QRSession]:
        """标记会话为已取消"""
        return await self.session_repo.mark_cancelled(session_id)
    
    async def update_session(self, session: QRSession) -> QRSession:
        """更新会话"""
        return await self.session_repo.update_session(session)
    
    async def get_session_stats(self) -> dict:
        """获取会话统计信息"""
        return await self.session_repo.get_session_stats()

