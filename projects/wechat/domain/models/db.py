# from sqlalchemy import (
#     Table,
#     Column,
#     BigInteger,
#     Integer,
#     String,
#     TIMESTAMP,
#     ForeignKey,
#     func,
# )

# from sqlalchemy import MetaData

# metadata = MetaData()
# SCHEMA = "wechat"

# # ... users_table, apps_table, user_app_links_table 的定义与上一回答完全相同 ...
# users_table = Table(
#     "user",
#     metadata,
#     Column("id", BigInteger, primary_key=True, index=True),
#     Column("nickname", String(255), comment="用户昵称"),
#     Column("avatar_url", String(1024), comment="用户头像链接"),
#     Column("phone_number", String(20), unique=True, nullable=True, comment="手机号"),
#     Column("status", Integer, default=1, comment="状态: 1-正常, 0-禁用"),
#     Column("created_at", TIMESTAMP, server_default=func.now(), comment="创建时间"),
#     Column("updated_at", TIMESTAMP, server_default=func.now(), onupdate=func.now(), comment="更新时间"),
#     schema=SCHEMA,
# )

# apps_table = Table(
#     "app",
#     metadata,
#     Column("id", BigInteger, primary_key=True, index=True),
#     Column("name", String(100), nullable=False),
#     Column("app_id", String(100), nullable=False),
#     Column("app_secret", String(100), nullable=False),
#     Column("created_at", TIMESTAMP, server_default=func.now(), comment="创建时间"),
#     Column("updated_at", TIMESTAMP, server_default=func.now(), onupdate=func.now(), comment="更新时间"),
#     schema=SCHEMA,
# )

# user_app_links_table = Table(
#     "app_user_links",
#     metadata,
#     Column("id", BigInteger, primary_key=True, index=True),
#     Column("user_id", BigInteger, ForeignKey(f"{SCHEMA}.user.id"), nullable=False),
#     Column("app_id", BigInteger, ForeignKey(f"{SCHEMA}.app.id"), nullable=False),
#     Column("union_id", String(128), nullable=True),
#     Column("open_id", String(128), nullable=False),
#     Column("created_at", TIMESTAMP, server_default=func.now(), comment="创建时间"),
#     Column("updated_at", TIMESTAMP, server_default=func.now(), onupdate=func.now(), comment="更新时间"),
#     schema=SCHEMA,
# )


