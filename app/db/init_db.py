# app/db/init_db.py
import os
import sys
import pathlib

# 将 app/ 目录加入 Python 路径（确保能导入 core, models）
APP_DIR = pathlib.Path(__file__).parent.parent  # app/ 目录
sys.path.insert(0, str(APP_DIR))

from core.config import settings
from models import Base

mode = (getattr(settings, "db_init_mode", "create") or "create").lower()
db_path = None
db_dir = None
if settings.database_url.startswith("sqlite:///"):
    db_path = settings.database_url.replace("sqlite:///", "")
    db_dir = os.path.dirname(db_path)
    if mode == "recreate" and os.path.exists(db_path):
        try:
            os.remove(db_path)
        except OSError:
            pass
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

def init_db():
    from sqlalchemy import create_engine, inspect, text
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False}
    )
    if mode == "recreate" and not settings.database_url.startswith("sqlite:///"):
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    if mode == "auto":
        if engine.dialect.name == "sqlite":
            insp = inspect(engine)
            with engine.begin() as conn:
                for name, table in Base.metadata.tables.items():
                    if name not in insp.get_table_names():
                        continue
                    existing = {c["name"] for c in insp.get_columns(name)}
                    for col in table.columns:
                        if col.name not in existing:
                            type_sql = col.type.compile(dialect=engine.dialect)
                            sql = f"ALTER TABLE {name} ADD COLUMN {col.name} {type_sql}"
                            if col.nullable:
                                sql += " NULL"
                            else:
                                sql += " NULL"
                            conn.execute(text(sql))
    print(f"✅ 数据库初始化成功！使用数据库: {settings.database_url}，模式: {mode}")

if __name__ == "__main__":
    init_db()
