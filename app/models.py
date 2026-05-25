from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base

class Url(Base):
    __tablename__ = "urls"

    code = Column(String(10), primary_key = True, index = True)
    long_url = Column(String, nullable = False)
    created_at = Column(DateTime(timezone = True), server_default=func.now())
    click_count = Column(Integer, default = 0)
    