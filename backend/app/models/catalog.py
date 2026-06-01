from sqlalchemy import Column, BigInteger, String, Float, Text, DateTime
from sqlalchemy.sql import func
from app.db.database import Base


class CatalogObject(Base):
    __tablename__ = "catalog"

    id          = Column(BigInteger, primary_key=True, autoincrement=True)
    norad_id    = Column(String(10), unique=True, index=True)
    name        = Column(String(255), nullable=False)
    object_type = Column(String(50))
    diameter_m  = Column(Float)
    mass_kg     = Column(Float)
    source      = Column(String(50))
    raw_tle1    = Column(Text)
    raw_tle2    = Column(Text)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), onupdate=func.now())