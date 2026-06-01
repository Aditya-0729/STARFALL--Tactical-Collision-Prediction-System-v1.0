from sqlalchemy import Column, BigInteger, Float, String, ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.sql import func
from app.db.database import Base


class Conjunction(Base):
    __tablename__ = "conjunctions"

    id              = Column(BigInteger, primary_key=True, autoincrement=True)
    primary_id      = Column(BigInteger, ForeignKey("catalog.id"))
    secondary_id    = Column(BigInteger, ForeignKey("catalog.id"))
    tca             = Column(TIMESTAMP(timezone=True), nullable=False)
    miss_distance_m = Column(Float, nullable=False)
    pc              = Column(Float, nullable=False)
    risk_level      = Column(String(20))
    computed_at     = Column(TIMESTAMP(timezone=True), server_default=func.now())