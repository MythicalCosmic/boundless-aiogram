def get_files(project_name: str, options: dict) -> dict:
    use_django = options.get("database") == "django"
    files = {}

    files["bot/handlers/__init__.py"] = '''from aiogram import Dispatcher
from bot.handlers.start import router as start_router
from bot.handlers.catalog import router as catalog_router
from bot.handlers.cart import router as cart_router
from bot.handlers.checkout import router as checkout_router


def register_all_handlers(dp: Dispatcher):
    dp.include_router(start_router)
    dp.include_router(catalog_router)
    dp.include_router(cart_router)
    dp.include_router(checkout_router)
'''

    files["bot/handlers/start.py"] = '''from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from bot.keyboards.main_menu import main_menu_keyboard

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        f"Welcome to our <b>Online Shop</b>, {message.from_user.full_name}!\\n\\n"
        "Browse products, add to cart, and checkout right here.\\n"
        "Use the menu below to get started.",
        reply_markup=main_menu_keyboard(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "<b>Shopping Guide</b>\\n\\n"
        "/catalog - Browse products\\n"
        "/cart - View your cart\\n"
        "/checkout - Place your order\\n"
        "/orders - Order history\\n"
        "/help - Show this help"
    )
'''

    files["bot/handlers/catalog.py"] = '''from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from bot.keyboards.catalog_kb import categories_keyboard, products_keyboard

router = Router(name="catalog")

CATALOG = {
    "electronics": {
        "name": "Electronics",
        "products": [
            {"id": "e1", "name": "Wireless Earbuds", "price": 29.99},
            {"id": "e2", "name": "Phone Case", "price": 12.99},
            {"id": "e3", "name": "USB-C Cable", "price": 8.99},
        ],
    },
    "clothing": {
        "name": "Clothing",
        "products": [
            {"id": "c1", "name": "T-Shirt", "price": 19.99},
            {"id": "c2", "name": "Hoodie", "price": 39.99},
            {"id": "c3", "name": "Cap", "price": 14.99},
        ],
    },
    "accessories": {
        "name": "Accessories",
        "products": [
            {"id": "a1", "name": "Backpack", "price": 49.99},
            {"id": "a2", "name": "Watch", "price": 79.99},
            {"id": "a3", "name": "Sunglasses", "price": 24.99},
        ],
    },
}


@router.message(Command("catalog"))
async def show_catalog(message: Message):
    await message.answer(
        "<b>Product Catalog</b>\\n\\nChoose a category:",
        reply_markup=categories_keyboard(CATALOG),
    )


@router.callback_query(F.data.startswith("shopcat_"))
async def show_category(callback: CallbackQuery):
    cat_key = callback.data.split("_", 1)[1]
    category = CATALOG.get(cat_key)
    if not category:
        await callback.answer("Category not found")
        return

    text = f"<b>{category['name']}</b>\\n\\n"
    for p in category["products"]:
        text += f"  {p['name']} -- ${p['price']:.2f}\\n"

    await callback.message.edit_text(text, reply_markup=products_keyboard(category["products"]))
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
        await message.answer("Your cart is empty. Browse /catalog to add products!")
        return
    total = sum(p["price"] * p.get("qty", 1) for p in cart)
    text = "<b>Your Cart</b>\\n\\n"
    for p in cart:
        qty = p.get("qty", 1)
        text += f"  {p['name']} x{qty} -- ${p['price'] * qty:.2f}\\n"
    text += f"\\n<b>Total: ${total:.2f}</b>\\n\\nUse /checkout to place your order."
    await message.answer(text)


@router.callback_query(F.data.startswith("buy_"))
async def add_to_cart(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_", 2)
    item_id = parts[1]
    item_name = parts[2] if len(parts) > 2 else item_id
    price_map = {
        "e1": 29.99, "e2": 12.99, "e3": 8.99,
        "c1": 19.99, "c2": 39.99, "c3": 14.99,
        "a1": 49.99, "a2": 79.99, "a3": 24.99,
    }
    data = await state.get_data()
    cart = data.get("cart", [])
    existing = next((i for i in cart if i["id"] == item_id), None)
    if existing:
        existing["qty"] = existing.get("qty", 1) + 1
    else:
        cart.append({"id": item_id, "name": item_name, "price": price_map.get(item_id, 0), "qty": 1})
    await state.update_data(cart=cart)
    await callback.answer(f"Added {item_name} to cart!")
'''

    files["bot/handlers/checkout.py"] = '''from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.states.checkout import CheckoutForm

router = Router(name="checkout")


@router.message(Command("checkout"))
async def start_checkout(message: Message, state: FSMContext):
    data = await state.get_data()
    cart = data.get("cart", [])
    if not cart:
        await message.answer("Your cart is empty!")
        return
    await state.set_state(CheckoutForm.name)
    await message.answer("Enter your <b>full name</b> for shipping:")


@router.message(CheckoutForm.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(CheckoutForm.phone)
    await message.answer("Enter your <b>phone number</b>:")


@router.message(CheckoutForm.phone)
async def process_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(CheckoutForm.address)
    await message.answer("Enter your <b>shipping address</b>:")


@router.message(CheckoutForm.address)
async def process_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    data = await state.get_data()
    cart = data.get("cart", [])
    total = sum(p["price"] * p.get("qty", 1) for p in cart)

    text = "<b>Order Summary</b>\\n\\n"
    for p in cart:
        qty = p.get("qty", 1)
        text += f"  {p['name']} x{qty} -- ${p['price'] * qty:.2f}\\n"
    text += f"\\nTotal: <b>${total:.2f}</b>\\n"
    text += f"Name: {data['name']}\\n"
    text += f"Phone: {data['phone']}\\n"
    text += f"Address: {data['address']}\\n\\n"
    text += "Order placed successfully! We will contact you for payment details."

    await state.clear()
    await message.answer(text)
'''

    files["bot/keyboards/main_menu.py"] = '''from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Catalog"), KeyboardButton(text="Cart")],
            [KeyboardButton(text="My Orders"), KeyboardButton(text="Help")],
        ],
        resize_keyboard=True,
    )
'''

    files["bot/keyboards/catalog_kb.py"] = '''from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def categories_keyboard(catalog: dict) -> InlineKeyboardMarkup:
    buttons = []
    for key, cat in catalog.items():
        buttons.append([InlineKeyboardButton(text=cat["name"], callback_data=f"shopcat_{key}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def products_keyboard(products: list) -> InlineKeyboardMarkup:
    buttons = []
    for p in products:
        buttons.append([
            InlineKeyboardButton(
                text=f"{p['name']} -- ${p['price']:.2f}",
                callback_data=f"buy_{p['id']}_{p['name']}",
            )
        ])
    buttons.append([InlineKeyboardButton(text="<< Back", callback_data="shopcat_back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
'''

    files["bot/states/checkout.py"] = '''from aiogram.fsm.state import State, StatesGroup


class CheckoutForm(StatesGroup):
    name = State()
    phone = State()
    address = State()
'''

    if not use_django:
        files["database/models/__init__.py"] = '''from database.models.base import Base
from database.models.user import User
from database.models.product import Product, Category
from database.models.order import Order, OrderItem
'''
        files["database/models/product.py"] = '''from sqlalchemy import String, Float, Boolean, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.models.base import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(100), unique=True)

    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    price: Mapped[float] = mapped_column(Float)
    image_file_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    category = relationship("Category", back_populates="products")
'''
        files["database/models/order.py"] = '''from datetime import datetime
from sqlalchemy import BigInteger, String, Float, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.models.base import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(50))
    address: Mapped[str] = mapped_column(String(500))
    total: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_name: Mapped[str] = mapped_column(String(255))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    price: Mapped[float] = mapped_column(Float)

    order = relationship("Order", back_populates="items")
'''

    return files
