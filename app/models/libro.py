from sqlalchemy import Column, Integer, String, Date, Boolean
from app.database.db import Base
from sqlalchemy.orm import relationship

class Libro(Base):
    __tablename__ = "Libros"

    Id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Cod_libro = Column(Integer, unique=True, nullable=False)
    Nombre_libro = Column(String(200), nullable=False)
    Fecha_publicacion = Column(Date, nullable=True)
    Autor = Column(String(100), nullable=True)
    Portada_Url = Column(String, nullable=True)
    Es_Infantil = Column(Boolean, default=False, nullable=False)
    
    copias = relationship("Copia", back_populates="libro_rel")