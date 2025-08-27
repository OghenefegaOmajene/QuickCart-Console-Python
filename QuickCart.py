import json
import os
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
import uuid

# Enums for better type safety and status management
class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"
    RIDER = "rider"

class OrderStatus(Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

# Base User class with common attributes
class User:
    def __init__(self, username: str, password: str, role: UserRole, name: str = ""):
        self.username = username
        self.password = password
        self.role = role
        self.name = name or username
        self.created_at = datetime.now()

    def to_dict(self):
        return {
            "username": self.username,
            "password": self.password,
            "role": self.role.value,
            "name": self.name,
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data):
        user = cls(data["username"], data["password"], UserRole(data["role"]), data["name"])
        user.created_at = datetime.fromisoformat(data["created_at"])
        return user
