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


# Product class for catalog management
class Product:
    def __init__(self, product_id: str, name: str, price: float, stock: int, category: str = "General"):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.stock = stock
        self.category = category

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "name": self.name,
            "price": self.price,
            "stock": self.stock,
            "category": self.category
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["product_id"], data["name"], data["price"], data["stock"], data["category"])

    def __str__(self):
        return f"[{self.product_id}] {self.name} - ${self.price:.2f} (Stock: {self.stock})"

# Order item for individual products in orders
class OrderItem:
    def __init__(self, product_id: str, product_name: str, price: float, quantity: int):
        self.product_id = product_id
        self.product_name = product_name
        self.price = price
        self.quantity = quantity
        self.subtotal = price * quantity

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "price": self.price,
            "quantity": self.quantity,
            "subtotal": self.subtotal
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["product_id"], data["product_name"], data["price"], data["quantity"])

    def __str__(self):
        return f"{self.product_name} x{self.quantity} = ${self.subtotal:.2f}"

