from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database.db import Base
from datetime import datetime

class Prestamo(Base):
    __tablename__ = "Prestamos"

    Id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Usuario = Column(Integer, ForeignKey("Usuarios.Id"), nullable=False)
    Fecha_prestamo = Column(DateTime, default=datetime.utcnow, nullable=False)

    usuario_rel = relationship("Usuario")
    detalles = relationship("DetallePrestamo", back_populates="prestamo", cascade="all, delete-orphan")