from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import Integer, String, DateTime

BaseModel = declarative_base()


class TimeLog(BaseModel):
    __tablename__ = 'time_log'
    id = Column(Integer, primary_key=True)
    type = Column(String(30))
    last_modify_time = Column(DateTime())


class StockBasic(BaseModel):
    __tablename__ = 'stock_basics'
    code = Column(String(30), primary_key=True)
