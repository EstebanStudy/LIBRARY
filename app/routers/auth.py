from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.core.dependencies import get_current_active_user, get_current_user  # ← clave aquí
from app.database.db import get_db
from app.crud.crud_usuario import get_usuario_by_correo, create_usuario
from app.schemas.usuario import UsuarioCreate, UsuarioResponse
from app.models.usuario import Usuario
from app.models.rol import Rol

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=dict)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    usuario = get_usuario_by_correo(db, correo=form_data.username)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not security.verify_password(form_data.password, usuario.Contraseña):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    rol = db.query(Rol).filter(Rol.Id == usuario.Rol).first()
    rol_nombre = rol.Nombre if rol else "sin_rol"

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=usuario.Correo, 
        role=rol_nombre, 
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  
        "role": rol_nombre  
    }

@router.post("/register", response_model=UsuarioResponse, status_code=201)
def register_usuario(
    usuario_in: UsuarioCreate,
    db: Session = Depends(get_db)
):
    if get_usuario_by_correo(db, correo=usuario_in.Correo):
        raise HTTPException(status_code=400, detail="Correo ya registrado")
    
    hashed_password = security.get_password_hash(usuario_in.Contraseña)
    usuario_in.Contraseña = hashed_password  
    
    nuevo_usuario = create_usuario(db=db, usuario=usuario_in)
    return nuevo_usuario

@router.get("/me", response_model=UsuarioResponse)
def read_users_me(current_user: Usuario = Depends(get_current_active_user)):
    return current_user