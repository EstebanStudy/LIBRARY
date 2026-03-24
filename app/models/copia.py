from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database.db import Base

class Copia(Base):
    __tablename__ = "Copias"

    Id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Libro = Column(Integer, ForeignKey("Libros.Id"), nullable=False)
    Notas = Column(String(255), nullable=True)
    Disponible = Column(Boolean, default=True, nullable=False)

    libro_rel = relationship("Libro", back_populates="copias")