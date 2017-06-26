# coding:utf-8
from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import Integer, String, DateTime

BaseModel = declarative_base()


class TimeLog(BaseModel):
    __tablename__ = 'time_log'
    type = Column(String(30), primary_key=True)
    last_modify_time = Column(DateTime())


class StockBasic(BaseModel):
    __tablename__ = 'stock_basics'
    code = Column(String(30), primary_key=True)


class ClmacdResult(BaseModel):
    __tablename__ = 'clmacd_result'
    id_time = Column(DateTime, primary_key=True)
    bp_count = Column(Integer)
    sp_count = Column(Integer)


class ClmacdBp(BaseModel):
    __tablename__ = 'clmacd_bp'
    id_time = Column(DateTime, primary_key=True)
    code = Column(String(50), primary_key=True)
    price = Column()


class ClmacdSp(BaseModel):
    __tablename__ = 'clmacd_sp'
    id_time = Column(DateTime, primary_key=True)
    code = Column(String(50), primary_key=True)
    price = Column()
