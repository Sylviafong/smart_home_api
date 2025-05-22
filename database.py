from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 创建PostgreSQL数据库连接
# 格式：postgresql://用户名:密码@主机:端口/数据库名
DATABASE_URL = "postgresql://postgres:password@localhost:5432/smart_home_db"

# 创建SQLAlchemy引擎
engine = create_engine(DATABASE_URL)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()

# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()