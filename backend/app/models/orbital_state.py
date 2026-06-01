from sqlalchemy import Column, BigInteger, Float, String, ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP
from app.db.database import Base


class OrbitalState(Base):
    __tablename__ = "orbital_states"

    time        = Column(TIMESTAMP(timezone=True), nullable=False, primary_key=True)
    object_id   = Column(BigInteger, ForeignKey("catalog.id"), nullable=False, primary_key=True)
    x_km        = Column(Float, nullable=False)
    y_km        = Column(Float, nullable=False)
    z_km        = Column(Float, nullable=False)
    vx_km_s     = Column(Float, nullable=False)
    vy_km_s     = Column(Float, nullable=False)
    vz_km_s     = Column(Float, nullable=False)
    altitude_km = Column(Float)
    coord_frame = Column(String(20), default="GEOCENTRIC")