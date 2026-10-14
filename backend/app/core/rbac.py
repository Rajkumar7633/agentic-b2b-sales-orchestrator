
from fastapi import Depends, HTTPException, status

from app.core.security import UserContext, get_current_user


class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: UserContext = Depends(get_current_user)) -> UserContext:
        if user.role not in self.allowed_roles and "ADMIN" not in user.role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required role: {self.allowed_roles}, your role: {user.role}"
            )
        return user


# Preset role checkers
require_admin = RoleChecker(["ADMIN"])
require_manager = RoleChecker(["ADMIN", "SALES_MANAGER"])
require_reviewer = RoleChecker(["ADMIN", "SALES_MANAGER", "REVIEWER"])
require_sales_rep = RoleChecker(["ADMIN", "SALES_MANAGER", "SALES_REP", "REVIEWER"])
