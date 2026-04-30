from sqlalchemy import Column, Integer, String
from app.database.db import Base

class Rol(Base):
    __tablename__ = "Roles"
    __table_args__ = {"implicit_returning": False}

    Id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Nombre = Column(String(50), nullable=False, unique=True)