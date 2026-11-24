
"""
Role-Based Security Module.

Provides basic role validation and access-control helpers.
"""

from enum import Enum
from fastapi import HTTPException, status


class UserRole(str, Enum):
    STUDENT = "student"
    TRAINER = "trainer"
    ADMIN = "admin"


def validate_role(role: str) -> UserRole:
    """Validate whether a role is supported."""

    try:
        return UserRole(role.lower().strip())

    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or unauthorized user role."
        )


def require_role(user_role: str, allowed_roles: list):
    """Check whether a user has permission for an operation."""

    role = validate_role(user_role)

    if role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource."
        )

    return role


def can_access_student_data(
    user_role: str,
    requested_student_id: str,
    current_user_id: str,
    assigned_student_ids: list = None
) -> bool:
    """
    Check student-data access.

    Students: Only their own records.
    Trainers: Only records of assigned students.
    Admins: Authorized administrative access.
    """

    role = validate_role(user_role)

    if role == UserRole.ADMIN:
        return True

    if role == UserRole.STUDENT:
        return requested_student_id == current_user_id

    if role == UserRole.TRAINER:
        return requested_student_id in (assigned_student_ids or [])

    return False
