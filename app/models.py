from sqlalchemy import Column, String, Integer, DateTime, func, ForeignKey
from app.database import Base

class Url(Base):
    __tablename__ = "urls"

    code = Column(String(10), primary_key=True, index=True)
    long_url = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    click_count = Column(Integer, default=0)

class Click(Base):
    __tablename__ = "clicks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(10), ForeignKey("urls.code"), nullable=False, index=True)
    clicked_at = Column(DateTime(timezone=True), server_default=func.now())
    ip = Column(String, nullable=True)
    country = Column(String, nullable=True)
    device = Column(String, nullable=True)
    browser = Column(String, nullable=True)
    