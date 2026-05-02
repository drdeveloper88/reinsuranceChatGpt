import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
import re

from app.core.config import settings

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class PasswordValidator:
    """Validate password strength"""
    
    MIN_LENGTH = 8
    PATTERN_UPPERCASE = r'[A-Z]'
    PATTERN_DIGIT = r'\d'
    PATTERN_SPECIAL = r'[!@#$%^&*(),.?":{}|<>]'
    
    @classmethod
    def validate(cls, password: str) -> tuple[bool, Optional[str]]:
        """Validate password and return (is_valid, error_message)"""
        if len(password) < cls.MIN_LENGTH:
            return False, f"Password must be at least {cls.MIN_LENGTH} characters"
        
        if not re.search(cls.PATTERN_UPPERCASE, password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(cls.PATTERN_DIGIT, password):
            return False, "Password must contain at least one digit"
        
        if not re.search(cls.PATTERN_SPECIAL, password):
            return False, "Password must contain at least one special character"
        
        return True, None


class TokenManager:
    """Manage JWT token creation and verification"""
    
    @staticmethod
    def create_access_token(
        data: Dict,
        expires_delta: Optional[timedelta] = None,
        token_type: str = "access"
    ) -> str:
        """Create JWT token"""
        try:
            to_encode = data.copy()
            to_encode["token_type"] = token_type
            
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
            
            to_encode.update({"exp": expire, "iat": datetime.utcnow()})
            encoded_jwt = jwt.encode(
                to_encode,
                settings.jwt_secret,
                algorithm=settings.jwt_algorithm
            )
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creating token: {str(e)}")
            raise

    @staticmethod
    def verify_token(token: str) -> str:
        """Verify JWT token and return subject"""
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=[settings.jwt_algorithm]
            )
            sub = payload.get("sub")
            if sub is None:
                raise JWTError("Missing sub claim")
            
            # Verify token type
            token_type = payload.get("token_type", "access")
            if token_type != "access":
                raise JWTError("Invalid token type")
            
            return sub
        except JWTError as e:
            logger.warning(f"Token verification failed: {str(e)}")
            raise


class PasswordManager:
    """Manage password hashing and verification"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password"""
        return pwd_context.verify(plain_password, hashed_password)


# Backwards compatibility functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Deprecated: Use TokenManager.create_access_token"""
    return TokenManager.create_access_token(data, expires_delta)


def verify_token(token: str):
    """Deprecated: Use TokenManager.verify_token"""
    return TokenManager.verify_token(token)
