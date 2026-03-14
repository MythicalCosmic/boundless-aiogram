def get_files(project_name: str, options: dict) -> dict:
    use_django = options.get("database") == "django"
    files = {}

    files["bot/handlers/__init__.py"] = '''from aiogram import Dispatcher
from bot.handlers.start import router as start_router
from bot.handlers.menu import router as menu_router
from bot.handlers.cart import router as cart_router
from bot.handlers.order import router as order_router


def register_all_handlers(dp: Dispatcher):
    dp.include_router(start_router)
    dp.include_router(menu_router)
    dp.include_router(cart_router)
    dp.include_router(order_router)
'''

    files["bot/handlers/start.py"] = '''from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from bot.keyboards.main_menu import main_menu_keyboard

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        f"Welcome to <b>FastFood Bot</b>, {message.from_user.full_name}!\\n\\n"
        "Browse our menu, add items to your cart, and place your order.\\n"
        "Fast food, delivered fast!",
        reply_markup=main_menu_keyboard(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "<b>How to Order</b>\\n\\n"
        "1. Browse the menu by category\\n"
        "2. Add items to your cart\\n"
        "3. Review your cart\\n"
        "4. Place your order\\n"
        "5. Track delivery status"
    )
'''

    files["bot/handlers/menu.py"] = '''from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from bot.keyboards.menu_kb import categories_keyboard, items_keyboard

router = Router(name="menu")

MENU = {
    "burgers": {
        "name": "Burgers",
        "items": [
            {"id": "b1", "name": "Classic Burger", "price": 5.99},
            {"id": "b2", "name": "Cheese Burger", "price": 6.99},
            {"id": "b3", "name": "Double Burger", "price": 8.99},
        ]
    },
    "pizza": {
        "name": "Pizza",
        "items": [
            {"id": "p1", "name": "Margherita", "price": 9.99},
            {"id": "p2", "name": "Pepperoni", "price": 11.99},
            {"id": "p3", "name": "Hawaiian", "price": 10.99},
        ]
    },
    "drinks": {
        "name": "Drinks",
        "items": [
            {"id": "d1", "name": "Cola", "price": 1.99},
            {"id": "d2", "name": "Juice", "price": 2.49},
            {"id": "d3", "name": "Water", "price": 0.99},
        ]
    },
    "sides": {
        "name": "Sides",
        "items": [
            {"id": "s1", "name": "French Fries", "price": 3.49},
            {"id": "s2", "name": "Onion Rings", "price": 3.99},
            {"id": "s3", "name": "Chicken Nuggets", "price": 4.99},
        ]
    },
}


@router.message(Command("menu"))
async def show_menu(message: Message):
    await message.answer(
        "<b>Our Menu</b>\\n\\nSelect a category:",
        reply_markup=categories_keyboard(MENU),
    )


@router.callback_query(F.data.startswith("cat_"))
async def show_category(callback: CallbackQuery):
    cat_key = callback.data.split("_", 1)[1]
    category = MENU.get(cat_key)
    if not category:
        await callback.answer("Category not found")
        return

    text = f"<b>{category['name']}</b>\\n\\n"
    for item in category["items"]:
        text += f"  {item['name']} -- ${item['price']:.2f}\\n"

    await callback.message.edit_text(
        text,
        reply_markup=items_keyboard(category["items"], cat_key),
    )
    await callback.answer()
'''

    files["bot/handlers/cart.py"] = '''from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

router = Router(name="cart")


@router.message(Command("cart"))
async def show_cart(message: Message, state: FSMContext):
    data = await state.get_data()
    cart = data.get("cart", [])

    if not cart:
        await message.answer("Your cart is empty. Browse /menu to add items!")
        return

    total = sum(item["price"] * item.get("qty", 1) for item in cart)
    text = "<b>Your Cart</b>\\n\\n"
    for item in cart:
        qty = item.get("qty", 1)
        text += f"  {item['name']} x{qty} -- ${item['price'] * qty:.2f}\\n"
    text += f"\\n<b>Total: ${total:.2f}</b>"

    await message.answer(text)


@router.callback_query(F.data.startswith("add_"))
async def add_to_cart(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_", 2)
    item_id = parts[1]
    item_name = parts[2] if len(parts) > 2 else item_id

    data = await state.get_data()
    cart = data.get("cart", [])

    # Simple price lookup (in production, use database)
    price_map = {
        "b1": 5.99, "b2": 6.99, "b3": 8.99,
        "p1": 9.99, "p2": 11.99, "p3": 10.99,
        "d1": 1.99, "d2": 2.49, "d3": 0.99,
        "s1": 3.49, "s2": 3.99, "s3": 4.99,
    }

    existing = next((i for i in cart if i["id"] == item_id), None)
    if existing:
        existing["qty"] = existing.get("qty", 1) + 1
    else:
        cart.append({"id": item_id, "name": item_name, "price": price_map.get(item_id, 0), "qty": 1})

    await state.update_data(cart=cart)
    await callback.answer(f"Added {item_name} to cart!")


@router.callback_query(F.data == "clear_cart")
async def clear_cart(callback: CallbackQuery, state: FSMContext):
    await state.update_data(cart=[])
    await callback.answer("Cart cleared!")
    await callback.message.edit_text("Your cart has been cleared.")
'''

    files["bot/handlers/order.py"] = '''from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.states.order import OrderForm

router = Router(name="order")


@router.message(Command("checkout"))
async def start_checkout(message: Message, state: FSMContext):
    data = await state.get_data()
    cart = data.get("cart", [])

    if not cart:
        await message.answer("Your cart is empty! Browse /menu first.")
        return

    await state.set_state(OrderForm.phone)
    await message.answer("Enter your <b>phone number</b> for the order:")


@router.message(OrderForm.phone)
async def process_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(OrderForm.address)
    await message.answer("Enter <b>delivery address</b>:")


@router.message(OrderForm.address)
async def process_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    data = await state.get_data()
    cart = data.get("cart", [])
    total = sum(item["price"] * item.get("qty", 1) for item in cart)

    text = "<b>Order Confirmation</b>\\n\\n"
    for item in cart:
        qty = item.get("qty", 1)
        text += f"  {item['name']} x{qty} -- ${item['price'] * qty:.2f}\\n"
    text += f"\\nTotal: <b>${total:.2f}</b>\\n"
    text += f"Phone: {data['phone']}\\n"
    text += f"Address: {data['address']}\\n\\n"
    text += "Your order has been placed! We will notify you when it is ready."

    await state.clear()
    await message.answer(text)
'''

    files["bot/keyboards/main_menu.py"] = '''from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Menu"), KeyboardButton(text="Cart")],
            [KeyboardButton(text="My Orders"), KeyboardButton(text="Help")],
        ],
        resize_keyboard=True,
    )
'''

    files["bot/keyboards/menu_kb.py"] = '''from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def categories_keyboard(menu: dict) -> InlineKeyboardMarkup:
    buttons = []
    for key, cat in menu.items():
        buttons.append([InlineKeyboardButton(text=cat["name"], callback_data=f"cat_{key}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def items_keyboard(items: list, category_key: str) -> InlineKeyboardMarkup:
    buttons = []
    for item in items:
        buttons.append([
            InlineKeyboardButton(
                text=f"{item['name']} -- ${item['price']:.2f}",
                callback_data=f"add_{item['id']}_{item['name']}",
            )
        ])
    buttons.append([InlineKeyboardButton(text="<< Back to Categories", callback_data="cat_back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
'''

    files["bot/states/order.py"] = '''from aiogram.fsm.state import State, StatesGroup


class OrderForm(StatesGroup):
    phone = State()
    address = State()
    confirm = State()
'''

    if not use_django:
        files["database/models/__init__.py"] = '''from database.models.base import Base
from database.models.user import User
from database.models.menu_item import MenuItem
from database.models.order import Order, OrderItem
'''
        files["database/models/menu_item.py"] = '''from sqlalchemy import String, Float, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from database.models.base import Base


class MenuItem(Base):
    __tablename__ = "menu_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(255))
    price: Mapped[float] = mapped_column(Float)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    def __repr__(self) -> str:
        return f"<MenuItem(name={self.name}, price={self.price})>"
'''
        files["database/models/order.py"] = '''from datetime import datetime
from sqlalchemy import BigInteger, String, Float, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.models.base import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    phone: Mapped[str] = mapped_column(String(50))
    address: Mapped[str] = mapped_column(String(500))
    total: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    items = relationship("OrderItem", back_populates="order")

    def __repr__(self) -> str:
        return f"<Order(id={self.id}, total={self.total}, status={self.status})>"


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    item_name: Mapped[str] = mapped_column(String(255))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    price: Mapped[float] = mapped_column(Float)

    order = relationship("Order", back_populates="items")
'''

    return files
