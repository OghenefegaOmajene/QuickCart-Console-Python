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


# Order class for managing customer orders
class Order:
    def __init__(self, order_id: str, customer_username: str, items: List[OrderItem], delivery_address: str):
        self.order_id = order_id
        self.customer_username = customer_username
        self.items = items
        self.delivery_address = delivery_address
        self.total_amount = sum(item.subtotal for item in items)
        self.status = OrderStatus.PENDING
        self.rider_username: Optional[str] = None
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def assign_rider(self, rider_username: str):
        self.rider_username = rider_username
        self.status = OrderStatus.ASSIGNED
        self.updated_at = datetime.now()

    def update_status(self, new_status: OrderStatus):
        self.status = new_status
        self.updated_at = datetime.now()

    def to_dict(self):
        return {
            "order_id": self.order_id,
            "customer_username": self.customer_username,
            "items": [item.to_dict() for item in self.items],
            "delivery_address": self.delivery_address,
            "total_amount": self.total_amount,
            "status": self.status.value,
            "rider_username": self.rider_username,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data):
        items = [OrderItem.from_dict(item_data) for item_data in data["items"]]
        order = cls(data["order_id"], data["customer_username"], items, data["delivery_address"])
        order.total_amount = data["total_amount"]
        order.status = OrderStatus(data["status"])
        order.rider_username = data.get("rider_username")
        order.created_at = datetime.fromisoformat(data["created_at"])
        order.updated_at = datetime.fromisoformat(data["updated_at"])
        return order

    def __str__(self):
        status_display = self.status.value.replace("_", " ").title()
        rider_info = f" (Rider: {self.rider_username})" if self.rider_username else ""
        return f"Order {self.order_id} - ${self.total_amount:.2f} - {status_display}{rider_info}"


# Data manager for JSON persistence
class DataManager:
    def __init__(self, data_file: str = "quickcart_data.json"):
        self.data_file = data_file
        self.data = self._load_data()

    def _load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return {"users": {}, "products": {}, "orders": {}}

    def save_data(self):
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")

    def add_user(self, user: User):
        self.data["users"][user.username] = user.to_dict()
        self.save_data()

    def get_user(self, username: str) -> Optional[User]:
        user_data = self.data["users"].get(username)
        return User.from_dict(user_data) if user_data else None

    def add_product(self, product: Product):
        self.data["products"][product.product_id] = product.to_dict()
        self.save_data()

    def get_product(self, product_id: str) -> Optional[Product]:
        product_data = self.data["products"].get(product_id)
        return Product.from_dict(product_data) if product_data else None

    def get_all_products(self) -> List[Product]:
        return [Product.from_dict(data) for data in self.data["products"].values()]

    def update_product_stock(self, product_id: str, new_stock: int):
        if product_id in self.data["products"]:
            self.data["products"][product_id]["stock"] = new_stock
            self.save_data()

    def add_order(self, order: Order):
        self.data["orders"][order.order_id] = order.to_dict()
        self.save_data()

    def update_order(self, order: Order):
        self.data["orders"][order.order_id] = order.to_dict()
        self.save_data()

    def get_order(self, order_id: str) -> Optional[Order]:
        order_data = self.data["orders"].get(order_id)
        return Order.from_dict(order_data) if order_data else None

    def get_orders_by_customer(self, username: str) -> List[Order]:
        return [Order.from_dict(data) for data in self.data["orders"].values() 
                if data["customer_username"] == username]

    def get_orders_by_rider(self, username: str) -> List[Order]:
        return [Order.from_dict(data) for data in self.data["orders"].values() 
                if data.get("rider_username") == username]

    def get_pending_orders(self) -> List[Order]:
        return [Order.from_dict(data) for data in self.data["orders"].values() 
                if data["status"] == OrderStatus.PENDING.value]

    def get_all_orders(self) -> List[Order]:
        return [Order.from_dict(data) for data in self.data["orders"].values()]


# Main application class
class QuickCartApp:
    def __init__(self):
        self.data_manager = DataManager()
        self.current_user: Optional[User] = None
        self._initialize_default_data()

    def _initialize_default_data(self):
        # Create default admin if none exists
        if not self.data_manager.get_user("admin"):
            admin = User("admin", "admin123", UserRole.ADMIN, "System Administrator")
            self.data_manager.add_user(admin)

        # Add some default products if none exist
        if not self.data_manager.get_all_products():
            default_products = [
                Product("P001", "Water Bottle", 1.50, 100, "Beverages"),
                Product("P002", "Energy Drink", 3.00, 50, "Beverages"),
                Product("P003", "Sandwich", 5.99, 30, "Food"),
                Product("P004", "Chips", 2.50, 75, "Snacks"),
                Product("P005", "Chocolate Bar", 1.99, 60, "Snacks")
            ]
            for product in default_products:
                self.data_manager.add_product(product)

    def run(self):
        print("🚀 Welcome to QuickCart - Ultra-Fast Micro Delivery!")
        print("=" * 50)
        
        while True:
            if not self.current_user:
                self._show_main_menu()
            else:
                if self.current_user.role == UserRole.ADMIN:
                    self._show_admin_menu()
                elif self.current_user.role == UserRole.USER:
                    self._show_user_menu()
                elif self.current_user.role == UserRole.RIDER:
                    self._show_rider_menu()

    def _show_main_menu(self):
        print("\n📋 MAIN MENU")
        print("1. Login")
        print("2. Register as Customer")
        print("3. Register as Rider")
        print("4. Exit")
        
        choice = self._get_input("Choose an option (1-4): ")
        
        if choice == "1":
            self._login()
        elif choice == "2":
            self._register_user()
        elif choice == "3":
            self._register_rider()
        elif choice == "4":
            print("Thank you for using QuickCart! Goodbye! 👋")
            exit()
        else:
            print("❌ Invalid option. Please try again.")

    def _login(self):
        print("\n🔐 LOGIN")
        username = self._get_input("Username: ")
        password = self._get_input("Password: ")
        
        user = self.data_manager.get_user(username)
        if user and user.password == password:
            self.current_user = user
            print(f"✅ Welcome back, {user.name}! ({user.role.value.title()})")
        else:
            print("❌ Invalid credentials. Please try again.")

    def _register_user(self):
        print("\n📝 CUSTOMER REGISTRATION")
        username = self._get_input("Choose a username: ")
        
        if self.data_manager.get_user(username):
            print("❌ Username already exists. Please choose another.")
            return
        
        password = self._get_input("Choose a password: ")
        name = self._get_input("Full name: ")
        
        user = User(username, password, UserRole.USER, name)
        self.data_manager.add_user(user)
        print("✅ Registration successful! You can now login.")

    def _register_rider(self):
        print("\n🏍️ RIDER REGISTRATION")
        username = self._get_input("Choose a username: ")
        
        if self.data_manager.get_user(username):
            print("❌ Username already exists. Please choose another.")
            return
        
        password = self._get_input("Choose a password: ")
        name = self._get_input("Full name: ")
        
        user = User(username, password, UserRole.RIDER, name)
        self.data_manager.add_user(user)
        print("✅ Rider registration successful! You can now login.")

    def _show_admin_menu(self):
        print(f"\n👨‍💼 ADMIN PANEL - Welcome {self.current_user.name}")
        print("1. Add Product")
        print("2. Restock Product")
        print("3. View All Products")
        print("4. View All Orders")
        print("5. View Order Statistics")
        print("6. Logout")
        
        choice = self._get_input("Choose an option (1-6): ")
        
        if choice == "1":
            self._add_product()
        elif choice == "2":
            self._restock_product()
        elif choice == "3":
            self._view_all_products()
        elif choice == "4":
            self._view_all_orders()
        elif choice == "5":
            self._view_order_statistics()
        elif choice == "6":
            self._logout()
        else:
            print("❌ Invalid option. Please try again.")

    def _add_product(self):
        print("\n➕ ADD NEW PRODUCT")
        product_id = self._get_input("Product ID: ").upper()
        
        if self.data_manager.get_product(product_id):
            print("❌ Product ID already exists.")
            return
        
        name = self._get_input("Product name: ")
        price = self._get_float_input("Price: $")
        stock = self._get_int_input("Initial stock: ")
        category = self._get_input("Category (optional): ") or "General"
        
        product = Product(product_id, name, price, stock, category)
        self.data_manager.add_product(product)
        print(f"✅ Product '{name}' added successfully!")

    def _restock_product(self):
        print("\n📦 RESTOCK PRODUCT")
        self._view_all_products()
        
        product_id = self._get_input("Enter Product ID to restock: ").upper()
        product = self.data_manager.get_product(product_id)
        
        if not product:
            print("❌ Product not found.")
            return
        
        print(f"Current stock for '{product.name}': {product.stock}")
        additional_stock = self._get_int_input("Enter additional stock to add: ")
        
        new_stock = product.stock + additional_stock
        self.data_manager.update_product_stock(product_id, new_stock)
        print(f"✅ Stock updated! New stock: {new_stock}")

    def _view_all_products(self):
        print("\n🛍️ PRODUCT CATALOG")
        products = self.data_manager.get_all_products()
        
        if not products:
            print("No products available.")
            return
        
        for product in products:
            print(f"  {product}")

    def _view_all_orders(self):
        print("\n📋 ALL ORDERS")
        orders = self.data_manager.get_all_orders()
        
        if not orders:
            print("No orders found.")
            return
        
        for order in orders:
            print(f"  {order}")
            print(f"    Customer: {order.customer_username}")
            print(f"    Address: {order.delivery_address}")
            print(f"    Created: {order.created_at.strftime('%Y-%m-%d %H:%M')}")
            print()

    def _view_order_statistics(self):
        print("\n📊 ORDER STATISTICS")
        orders = self.data_manager.get_all_orders()
        
        if not orders:
            print("No orders to analyze.")
            return
        
        total_orders = len(orders)
        total_revenue = sum(order.total_amount for order in orders)
        
        status_counts = {}
        for order in orders:
            status = order.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"Total Orders: {total_orders}")
        print(f"Total Revenue: ${total_revenue:.2f}")
        print("Order Status Breakdown:")
        for status, count in status_counts.items():
            print(f"  {status.replace('_', ' ').title()}: {count}")

    def _show_user_menu(self):
        print(f"\n🛒 CUSTOMER PORTAL - Welcome {self.current_user.name}")
        print("1. Browse Products")
        print("2. Place Order")
        print("3. View My Orders")
        print("4. Logout")
        
        choice = self._get_input("Choose an option (1-4): ")
        
        if choice == "1":
            self._browse_products()
        elif choice == "2":
            self._place_order()
        elif choice == "3":
            self._view_my_orders()
        elif choice == "4":
            self._logout()
        else:
            print("❌ Invalid option. Please try again.")

    def _browse_products(self):
        print("\n🛍️ AVAILABLE PRODUCTS")
        products = self.data_manager.get_all_products()
        available_products = [p for p in products if p.stock > 0]
        
        if not available_products:
            print("No products available at the moment.")
            return
        
        for product in available_products:
            print(f"  {product}")

    def _place_order(self):
        print("\n🛒 PLACE ORDER")
        products = self.data_manager.get_all_products()
        available_products = [p for p in products if p.stock > 0]
        
        if not available_products:
            print("❌ No products available for order.")
            return
        
        self._browse_products()
        
        cart = []
        while True:
            product_id = self._get_input("\nEnter Product ID to add to cart (or 'done' to finish): ").upper()
            
            if product_id.lower() == 'done':
                break
            
            product = self.data_manager.get_product(product_id)
            if not product:
                print("❌ Product not found.")
                continue
            
            if product.stock <= 0:
                print("❌ Product out of stock.")
                continue
            
            quantity = self._get_int_input(f"Enter quantity for {product.name} (max {product.stock}): ")
            
            if quantity <= 0 or quantity > product.stock:
                print("❌ Invalid quantity.")
                continue
            
            cart_item = OrderItem(product.product_id, product.name, product.price, quantity)
            cart.append(cart_item)
            print(f"✅ Added {cart_item}")
        
        if not cart:
            print("❌ No items in cart.")
            return
        
        # Display cart summary
        print("\n🛒 CART SUMMARY")
        total = sum(item.subtotal for item in cart)
        for item in cart:
            print(f"  {item}")
        print(f"Total: ${total:.2f}")
        
        confirm = self._get_input("Confirm order? (y/n): ").lower()
        if confirm != 'y':
            print("❌ Order cancelled.")
            return
        
        delivery_address = self._get_input("Enter delivery address: ")
        
        # Create order and update stock
        order_id = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}"
        order = Order(order_id, self.current_user.username, cart, delivery_address)
        
        # Update product stock
        for item in cart:
            product = self.data_manager.get_product(item.product_id)
            new_stock = product.stock - item.quantity
            self.data_manager.update_product_stock(item.product_id, new_stock)
        
        self.data_manager.add_order(order)
        print(f"✅ Order placed successfully! Order ID: {order_id}")

    def _view_my_orders(self):
        print("\n📋 MY ORDERS")
        orders = self.data_manager.get_orders_by_customer(self.current_user.username)
        
        if not orders:
            print("You have no orders yet.")
            return
        
        for order in orders:
            print(f"  {order}")
            print(f"    Address: {order.delivery_address}")
            print(f"    Items: {len(order.items)} items")
            print(f"    Ordered: {order.created_at.strftime('%Y-%m-%d %H:%M')}")
            print()

    def _show_rider_menu(self):
        print(f"\n🏍️ RIDER PORTAL - Welcome {self.current_user.name}")
        print("1. View Available Orders")
        print("2. Accept Order")
        print("3. View My Orders")
        print("4. Update Order Status")
        print("5. Logout")
        
        choice = self._get_input("Choose an option (1-5): ")
        
        if choice == "1":
            self._view_available_orders()
        elif choice == "2":
            self._accept_order()
        elif choice == "3":
            self._view_my_rider_orders()
        elif choice == "4":
            self._update_order_status()
        elif choice == "5":
            self._logout()
        else:
            print("❌ Invalid option. Please try again.")

    def _view_available_orders(self):
        print("\n📋 AVAILABLE ORDERS")
        pending_orders = self.data_manager.get_pending_orders()
        
        if not pending_orders:
            print("No orders available for pickup.")
            return
        
        for order in pending_orders:
            print(f"  {order}")
            print(f"    Customer: {order.customer_username}")
            print(f"    Address: {order.delivery_address}")
            print(f"    Items: {len(order.items)} items")
            print()

    def _accept_order(self):
        print("\n✋ ACCEPT ORDER")
        pending_orders = self.data_manager.get_pending_orders()
        
        if not pending_orders:
            print("❌ No orders available for pickup.")
            return
        
        self._view_available_orders()
        
        order_id = self._get_input("Enter Order ID to accept: ").upper()
        order = self.data_manager.get_order(order_id)
        
        if not order:
            print("❌ Order not found.")
            return
        
        if order.status != OrderStatus.PENDING:
            print("❌ Order is not available for pickup.")
            return
        
        order.assign_rider(self.current_user.username)
        self.data_manager.update_order(order)
        print(f"✅ Order {order_id} accepted! You can now start delivery.")

    def _view_my_rider_orders(self):
        print("\n📋 MY ASSIGNED ORDERS")
        my_orders = self.data_manager.get_orders_by_rider(self.current_user.username)
        
        if not my_orders:
            print("You have no assigned orders.")
            return
        
        for order in my_orders:
            print(f"  {order}")
            print(f"    Customer: {order.customer_username}")
            print(f"    Address: {order.delivery_address}")
            print(f"    Assigned: {order.updated_at.strftime('%Y-%m-%d %H:%M')}")
            print()

    def _update_order_status(self):
        print("\n📝 UPDATE ORDER STATUS")
        my_orders = self.data_manager.get_orders_by_rider(self.current_user.username)
        active_orders = [o for o in my_orders if o.status not in [OrderStatus.DELIVERED, OrderStatus.CANCELLED]]
        
        if not active_orders:
            print("❌ No active orders to update.")
            return
        
        print("Your active orders:")
        for order in active_orders:
            print(f"  {order}")
        
        order_id = self._get_input("Enter Order ID to update: ").upper()
        order = self.data_manager.get_order(order_id)
        
        if not order or order.rider_username != self.current_user.username:
            print("❌ Order not found or not assigned to you.")
            return
        
        print(f"Current status: {order.status.value.replace('_', ' ').title()}")
        print("Available status updates:")
        
        if order.status == OrderStatus.ASSIGNED:
            print("1. Start Delivery (In Progress)")
        elif order.status == OrderStatus.IN_PROGRESS:
            print("1. Mark as Delivered")
            print("2. Cancel Order")
        
        choice = self._get_input("Choose status update: ")
        
        if order.status == OrderStatus.ASSIGNED and choice == "1":
            order.update_status(OrderStatus.IN_PROGRESS)
            print("✅ Status updated to 'In Progress'")
        elif order.status == OrderStatus.IN_PROGRESS:
            if choice == "1":
                order.update_status(OrderStatus.DELIVERED)
                print("✅ Order marked as delivered!")
            elif choice == "2":
                order.update_status(OrderStatus.CANCELLED)
                print("⚠️ Order cancelled.")
        else:
            print("❌ Invalid choice.")
            return
        
        self.data_manager.update_order(order)

    def _logout(self):
        print(f"👋 Goodbye, {self.current_user.name}!")
        self.current_user = None

    def _get_input(self, prompt: str) -> str:
        try:
            return input(prompt).strip()
        except (KeyboardInterrupt, EOFError):
            print("\n👋 Goodbye!")
            exit()

    def _get_int_input(self, prompt: str) -> int:
        while True:
            try:
                return int(self._get_input(prompt))
            except ValueError:
                print("❌ Please enter a valid number.")

    def _get_float_input(self, prompt: str) -> float:
        while True:
            try:
                return float(self._get_input(prompt))
            except ValueError:
                print("❌ Please enter a valid number.")

# Entry point
if __name__ == "__main__":
    try:
        app = QuickCartApp()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Thank you for using QuickCart!")
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        print("Please restart the application.")