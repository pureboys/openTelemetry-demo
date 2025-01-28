from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

DATABASE_URL = "mysql+pymysql://myuser:mypassword@localhost:3306/mydb"
# 创建数据库引擎
engine = create_engine(DATABASE_URL)
# 初始化 SQLAlchemy Instrumentor
SQLAlchemyInstrumentor().instrument(engine=engine)

# 创建数据库会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Students(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer, index=True)
    created_at = Column(DateTime, index=True)
    updated_at = Column(DateTime, index=True)

# 依赖项：获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
