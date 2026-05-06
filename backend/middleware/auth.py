"""
Middleware de autenticación JWT para FastAPI
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import logging
from datetime import datetime, timedelta
from pydantic import BaseModel
from config import SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRATION_HOURS

logger = logging.getLogger(__name__)

# Esquema de seguridad HTTP Bearer
security = HTTPBearer()


class User(BaseModel):
    """Modelo de usuario autenticado"""
    user_id: str
    role: str = "user"


def generate_token(user_id: str, role: str = "user") -> str:
    """
    Genera un JWT token para un usuario
    
    Args:
        user_id: ID del usuario
        role: Rol del usuario (user, admin, etc.)
    
    Returns:
        Token JWT como string
    """
    payload = {
        'user_id': user_id,
        'role': role,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> dict:
    """
    Verifica y decodifica un JWT token
    
    Args:
        token: Token JWT a verificar
    
    Returns:
        Payload del token decodificado
    
    Raises:
        jwt.ExpiredSignatureError: Si el token ha expirado
        jwt.InvalidTokenError: Si el token es inválido
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token expirado")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        logger.warning(f"Token inválido: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """
    Dependency para obtener el usuario actual desde el token JWT
    
    Uso en endpoints:
        @app.get("/protected")
        async def protected_route(current_user: User = Depends(get_current_user)):
            return {"user_id": current_user.user_id}
    
    Args:
        credentials: Credenciales HTTP Bearer del header Authorization
    
    Returns:
        Usuario autenticado
    
    Raises:
        HTTPException: Si el token es inválido o ha expirado
    """
    token = credentials.credentials
    
    try:
        payload = verify_token(token)
        user = User(
            user_id=payload['user_id'],
            role=payload.get('role', 'user')
        )
        logger.debug(f"Usuario autenticado: {user.user_id}")
        return user
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al verificar token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo validar las credenciales",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_role(required_role: str):
    """
    Dependency para requerir un rol específico
    
    Uso:
        @app.get("/admin")
        async def admin_route(
            current_user: User = Depends(get_current_user),
            _: None = Depends(require_role("admin"))
        ):
            return {"message": "Admin access"}
    
    Args:
        required_role: Rol requerido para acceder al endpoint
    
    Returns:
        Dependency function
    """
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role:
            logger.warning(
                f"Usuario {current_user.user_id} intentó acceder a recurso "
                f"que requiere rol {required_role} (tiene {current_user.role})"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permisos insuficientes"
            )
        return None
    
    return role_checker
