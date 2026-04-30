from datetime import datetime, timedelta, timezone
from typing import Any, Union
import hashlib
import uuid
import logging

from jose import jwt

from app.core.config import settings

HASH_ALGORITHM = 'sha256'

def _normalize_bytes(value: bytes | memoryview | str) -> bytes:
    if isinstance(value, memoryview):
        return bytes(value)
    if isinstance(value, str):
        return value.encode('utf-8')
    return value

def _hash_password_with_salt(password: str, salt: str | uuid.UUID) -> bytes:
    salt_text = str(salt).upper()
    # SQL Server HASHBYTES on NVARCHAR uses UTF-16LE encoding
    digest = hashlib.new(HASH_ALGORITHM, (password + salt_text).encode('utf-16le'))
    return digest.digest()

def verify_password(
    plain_password: str,
    salt: str | uuid.UUID | None = None,
    hashed_password: bytes | memoryview | str | None = None,
    legacy_hash: str | None = None
) -> bool:
    """Verifica contraseña con salt y SHA-256, o con hashes legacy."""
    try:
        if isinstance(hashed_password, str):
            if hashed_password.startswith('$argon2'):
                from argon2 import PasswordHasher
                from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError

                argon2_hasher = PasswordHasher()
                try:
                    return argon2_hasher.verify(hashed_password, plain_password)
                except (VerifyMismatchError, VerificationError, InvalidHashError):
                    return False
            if hashed_password.startswith('$2'):
                import bcrypt
                try:
                    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
                except Exception:
                    return False

        if salt is not None and hashed_password is not None:
            return _hash_password_with_salt(plain_password, salt) == _normalize_bytes(hashed_password)

        if legacy_hash is not None:
            return verify_password(plain_password, None, legacy_hash, None)

        return False
    except Exception as e:
        logging.debug(f"Password verification error: {str(e)}")
        return False

def get_password_hash(password: str) -> tuple[str, bytes]:
    """Genera salt y hash SHA-256 para almacenar en la base de datos."""
    salt = uuid.uuid4()
    salt_text = str(salt).upper()
    return salt_text, _hash_password_with_salt(password, salt_text)

def create_access_token(
    subject: Union[str, Any], role: str, expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {
        "sub": str(subject),        
        "role": role,           
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt