from sqlalchemy import Column, Integer, String, BigInteger
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    language_code = Column(String, default="en")

class ButtonStatistic(Base):
    __tablename__ = "button_statistics"

    id = Column(Integer, primary_key=True, index=True)
    button_key = Column(String, unique=True, index=True)
    click_count = Column(Integer, default=0) 