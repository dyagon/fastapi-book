import asyncio
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DB_URI = "postgresql+asyncpg://admin:admin123@localhost:25432/fastapi_book"
SCHEMA_TO_DROP = ["public", "chatroom", "hospital", "wechat", "oauth2"]
ALEMBIC_VERSIONS_DIR = Path("alembic/versions")


async def schema_exists(engine, schema_name):
    """检查 schema 是否存在"""
    async with engine.begin() as conn:
        query = text(
            """
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name = :schema_name
        """
        )
        result = await conn.execute(query, {"schema_name": schema_name})
        return result.fetchone() is not None


async def create_schema(engine, schema_name):
    """创建 schema"""
    async with engine.begin() as conn:
        print(f"正在创建 schema: {schema_name}")
        await conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))
        print(f"✓ Schema '{schema_name}' 创建成功")


async def get_tables_in_schema(engine, schema_name):
    """获取指定 schema 下的所有表名"""
    async with engine.begin() as conn:
        # 查询指定 schema 下的所有表
        query = text(
            """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = :schema_name
            AND table_type = 'BASE TABLE'
        """
        )
        result = await conn.execute(query, {"schema_name": schema_name})
        tables = [row[0] for row in result.fetchall()]
        return tables


async def process_schema(schema_name: str):
    """处理单个 schema：检查是否存在，不存在则创建，存在则清空表"""
    engine = create_async_engine(DB_URI)

    try:
        print(f"\n=== 处理 Schema: {schema_name} ===")

        # 检查 schema 是否存在
        exists = await schema_exists(engine, schema_name)

        if not exists:
            print(f"Schema '{schema_name}' 不存在，正在创建...")
            await create_schema(engine, schema_name)
            print(f"✓ Schema '{schema_name}' 处理完成（新创建）")
            return

        print(f"Schema '{schema_name}' 已存在，正在清空其中的表...")

        # 获取指定 schema 下的所有表
        tables_to_drop = await get_tables_in_schema(engine, schema_name)

        if not tables_to_drop:
            print(f"Schema '{schema_name}' 下没有找到任何表")
            print(f"✓ Schema '{schema_name}' 处理完成（无表需要删除）")
            return

        print(f"在 schema '{schema_name}' 下找到以下表:")
        for table in tables_to_drop:
            print(f"  - {table}")

        # 删除所有表
        async with engine.begin() as conn:
            for table_name in tables_to_drop:
                print(f"正在删除表: {schema_name}.{table_name}")
                await conn.execute(
                    text(f'DROP TABLE IF EXISTS "{schema_name}"."{table_name}" CASCADE')
                )
                print(f"✓ 表 {schema_name}.{table_name} 删除成功")

        print(f"✓ Schema '{schema_name}' 处理完成（已清空所有表）")

    except Exception as e:
        print(f"处理 schema '{schema_name}' 时发生错误: {e}")
        raise
    finally:
        await engine.dispose()


async def main():
    """主函数"""
    print("开始处理数据库 Schema...")
    print(f"目标 Schema: {SCHEMA_TO_DROP}")
    print("处理逻辑：如果 schema 不存在则创建，如果存在则清空其中的表")

    # 确认操作
    confirm = input(f"确认要处理这些 schema 吗？(y/N): ")
    if confirm.lower() != "y":
        print("操作已取消")
        return

    for schema_name in SCHEMA_TO_DROP:
        await process_schema(schema_name)

    # 删除 alembic 下面所有的 versions
    for version_file in ALEMBIC_VERSIONS_DIR.glob("*.py"):
        version_file.unlink()
        print(f"✓ 删除 alembic 版本文件: {version_file}")

    print(f"\n🎉 所有 schema 处理完成！")


if __name__ == "__main__":
    asyncio.run(main())
