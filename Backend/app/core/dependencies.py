from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.db import get_db
from app.crud.crud_usuario import get_usuario_by_correo
from app.models.usuario import Usuario
from app.models.rol import Rol

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        correo: str = payload.get("sub")
        if correo is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    usuario = get_usuario_by_correo(db, correo=correo)
    if usuario is None:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return usuario


def get_current_active_user(current_user: Usuario = Depends(get_current_user)):
    return current_user


def require_role(required_role: str):
    def role_checker(
        current_user: Usuario = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        rol = db.query(Rol).filter(Rol.Id == current_user.Rol).first()
        if rol is None or rol.Nombre != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Se requiere el rol: {required_role} (tienes: {rol.Nombre if rol else 'None'})"
            )
        return current_user
    return role_checker


def require_any_role(allowed_roles: list[str]):
    """
    Dependencia que permite el acceso si el usuario tiene ALGUNO de los roles permitidos.
    Uso: Depends(require_any_role(["Administrador", "Usuario", "Niños"]))
    """
    def role_checker(
        current_user: Usuario = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        rol = db.query(Rol).filter(Rol.Id == current_user.Rol).first()
        if rol is None or rol.Nombre not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Se requiere uno de los roles: {', '.join(allowed_roles)} (tienes: {rol.Nombre if rol else 'None'})"
            )
        return current_user
    return role_checker