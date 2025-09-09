"""会话仓库 - Redis实现"""
import json
from typing import Optional, List
from redis.asyncio import Redis
from ..models.session import QRSession, QRCodeStatus, UserInfo


class SessionRepository:
    
    def __init__(self, redis_client: Redis):
        self._redis = redis_client
        self._key_prefix = "wechat:session:"
    
    def _get_key(self, session_id: str) -> str:
        """生成Redis键名"""
        return f"{self._key_prefix}{session_id}"
    
    async def create_session(self, session: QRSession) -> QRSession:
        """创建新会话"""
        redis_client = self._redis
        key = self._get_key(session.session_id)
        
        # 设置过期时间
        expire_seconds = int(session.expires_at.timestamp() / 1000)
        
        # 存储会话数据
        session_data = session.model_dump_json()
        await redis_client.setex(key, expire_seconds, session_data)
        
        return session
    
    async def get_session(self, session_id: str) -> Optional[QRSession]:
        """获取会话"""
        redis_client = self._redis
        key = self._get_key(session_id)
        
        session_data = await redis_client.get(key)
        if not session_data:
            return None
        
        try:
            session_dict = json.loads(session_data)
            return QRSession.model_validate(session_dict)
        except (json.JSONDecodeError, ValueError):
            # 数据损坏，删除
            await redis_client.delete(key)
            return None
    
    async def update_session(self, session: QRSession) -> QRSession:
        """更新会话"""
        redis_client = self._redis
        key = self._get_key(session.session_id)
        
        # 检查会话是否存在
        if not await redis_client.exists(key):
            raise ValueError(f"会话 {session.session_id} 不存在")
        
        # 重新设置过期时间
        expire_seconds = int((session.expires_at - session.created_at).total_seconds())
        session_data = session.model_dump_json()
        await redis_client.setex(key, expire_seconds, session_data)
        
        return session
    
    async def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        redis_client = self._redis
        key = self._get_key(session_id)
        
        result = await redis_client.delete(key)
        return result > 0
    
    async def mark_scanned(self, session_id: str, user_info: UserInfo) -> Optional[QRSession]:
        """标记会话为已扫描"""
        session = await self.get_session(session_id)
        if not session:
            return None
        
        try:
            session.mark_scanned(user_info)
            return await self.update_session(session)
        except ValueError:
            return None
    
    async def mark_confirmed(self, session_id: str, code: str) -> Optional[QRSession]:
        """标记会话为已确认"""
        session = await self.get_session(session_id)
        if not session:
            return None
        
        try:
            session.mark_confirmed(code)
            return await self.update_session(session)
        except ValueError:
            return None
    
    async def mark_cancelled(self, session_id: str) -> Optional[QRSession]:
        """标记会话为已取消"""
        session = await self.get_session(session_id)
        if not session:
            return None
        
        try:
            session.mark_cancelled()
            return await self.update_session(session)
        except ValueError:
            return None
    
    async def mark_expired(self, session_id: str) -> Optional[QRSession]:
        """标记会话为已过期"""
        session = await self.get_session(session_id)
        if not session:
            return None
        
        session.mark_expired()
        return await self.update_session(session)
    
    async def cleanup_expired_sessions(self) -> int:
        """清理过期会话"""
        redis_client = self._redis
        pattern = f"{self._key_prefix}*"
        
        # 获取所有会话键
        keys = await redis_client.keys(pattern)
        cleaned_count = 0
        
        for key in keys:
            session_data = await redis_client.get(key)
            if not session_data:
                continue
            
            try:
                session_dict = json.loads(session_data)
                session = QRSession.model_validate(session_dict)
                
                # 检查是否过期
                if session.is_expired() and session.status not in [QRCodeStatus.CONFIRMED, QRCodeStatus.CANCELLED]:
                    session.mark_expired()
                    await self.update_session(session)
                    cleaned_count += 1
                    
            except (json.JSONDecodeError, ValueError):
                # 数据损坏，删除
                await redis_client.delete(key)
                cleaned_count += 1
        
        return cleaned_count
    
    async def get_session_stats(self) -> dict:
        """获取会话统计信息"""
        redis_client = self._redis
        pattern = f"{self._key_prefix}*"
        keys = await redis_client.keys(pattern)
        
        stats = {
            "total": len(keys),
            "unscanned": 0,
            "scanned": 0,
            "confirmed": 0,
            "expired": 0,
            "cancelled": 0,
        }
        
        for key in keys:
            session_data = await redis_client.get(key)
            if not session_data:
                continue
            
            try:
                session_dict = json.loads(session_data)
                session = QRSession.model_validate(session_dict)
                status_key = session.status.value
                if status_key in stats:
                    stats[status_key] += 1
            except (json.JSONDecodeError, ValueError):
                continue
        
        return stats
    