"""用户相关路由"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.dto import UserInfoResponse

router = APIRouter(prefix="/wechat/user", tags=["User"])


@router.get("/list")
async def list_users(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(10, ge=1, le=100, description="限制记录数"),
    db: Session = Depends(get_db)
):
    """获取用户列表"""
    users = db.query(User).offset(skip).limit(limit).all()
    
    return {
        "users": [
            {
                "id": user.id,
                "openid": user.openid,
                "nickname": user.nickname,
                "avatar_url": user.avatar_url,
                "gender": user.gender,
                "city": user.city,
                "province": user.province,
                "country": user.country,
                "created_at": user.created_at
            }
            for user in users
        ],
        "total": db.query(User).count(),
        "skip": skip,
        "limit": limit
    }


@router.get("/{openid}")
async def get_user_by_openid(
    openid: str,
    db: Session = Depends(get_db)
):
    """根据openid获取用户信息"""
    user = db.query(User).filter(User.openid == openid).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return {
        "id": user.id,
        "openid": user.openid,
        "unionid": user.unionid,
        "nickname": user.nickname,
        "avatar_url": user.avatar_url,
        "gender": user.gender,
        "city": user.city,
        "province": user.province,
        "country": user.country,
        "language": user.language,
        "created_at": user.created_at,
        "updated_at": user.updated_at
    }


@router.get("/stats/summary")
async def get_user_stats(db: Session = Depends(get_db)):
    """获取用户统计信息"""
    total_users = db.query(User).count()
    
    # 按性别统计
    gender_stats = db.query(User.gender, db.func.count(User.id)).group_by(User.gender).all()
    
    # 按省份统计（取前10）
    province_stats = db.query(
        User.province, 
        db.func.count(User.id)
    ).filter(User.province.isnot(None)).group_by(User.province).order_by(
        db.func.count(User.id).desc()
    ).limit(10).all()
    
    return {
        "total_users": total_users,
        "gender_distribution": {
            "unknown": next((count for gender, count in gender_stats if gender == 0), 0),
            "male": next((count for gender, count in gender_stats if gender == 1), 0),
            "female": next((count for gender, count in gender_stats if gender == 2), 0)
        },
        "top_provinces": [
            {"province": province, "count": count}
            for province, count in province_stats
        ]
    }
