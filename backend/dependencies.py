# ==== backend/dependencies.py ====
from fastapi import Depends, HTTPException, status
from typing import List

from .routers.auth import get_current_user_from_token
from .schemas.auth import UserPayload, UserRole
from .utils.logger import setup_logging

logger = setup_logging()

def require_roles(required_roles: List[UserRole]):
    """
    A dependency function that checks if the current user has one of the required roles.
    
    Args:
        required_roles (List[UserRole]): A list of roles that are allowed to access the endpoint.
        
    Returns:
        function: A dependency that raises HTTPException if the user's role is not allowed.
    """
    async def role_checker(current_user: UserPayload = Depends(get_current_user_from_token)):
        if current_user.role not in required_roles:
            logger.warning(f"User {current_user.email} with role {current_user.role} attempted to access restricted endpoint (required: {required_roles}).")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not authorized. Required roles: {', '.join([role.value for role in required_roles])}"
            )
        return current_user
    return role_checker

# Helper dependency for just getting the current user without role restriction
def get_current_user(current_user: UserPayload = Depends(get_current_user_from_token)):
    """
    A simple dependency to retrieve the current authenticated user's payload.
    """
    return current_user