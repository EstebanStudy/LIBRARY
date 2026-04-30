from sqlalchemy import Column, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.database.db import Base

class DetallePrestamo(Base):
    __tablename__ = "Detalles_Prestamo"
    __table_args__ = {"implicit_returning": False}

    Id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Prestamo = Column(Integer, ForeignKey("Prestamos.Id", ondelete="CASCADE"), nullable=False)
    Copia = Column(Integer, ForeignKey("Copias.Id"), nullable=False)
    Fecha_entrega_esperada = Column(Date, nullable=False)
    Fecha_devolucion_real = Column(Date, nullable=True)

    prestamo = relationship("Prestamo", back_populates="detalles")   
    copia_rel = relationship("Copia")