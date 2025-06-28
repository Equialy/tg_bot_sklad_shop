from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.utils import markdown
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.filters.chat_types import ChatTypeFilter, IsAdmin
from src.bot.handlers.admin_handlers.handler_category import admin_router_category
from src.bot.handlers.admin_handlers.update_router import admin_router_update
from src.bot.keyboards.inline_keyboards import get_callback_btns
from src.bot.keyboards.reply_keyboard import get_reply_keyboard
from src.bot.schemas.product_schema import ProductSchemaRead, ProductSchemaBase
from src.bot.states.states import AddProduct

from src.infrastructure.database.repositories.categories_repo import (
    CategoryRepositoryImpl,
)
from src.infrastructure.database.repositories.products_repo import ProductsRepoImpl

admin_router = Router(name=__name__)
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())
admin_router.include_routers(admin_router_category, admin_router_update)

ADMIN_KB = get_reply_keyboard(
    "Добавить товар",
    "Добавить категорию",
    "Каталог",
    "Изменить товар",
    "Удалить товар",
    placeholder="Выберите действие",
    size=(
        2,
        1,
    ),
)
ADMIN_INLINE_KB = get_callback_btns(
    btns={
        "Добавить товар": "add_product",
        "Добавить категорию": "add_category",
        "Каталог": "catalog_products",
        "Изменить товар": "update_product",
        "Удалить товар": "delete_product",
    }
)


@admin_router.message(Command("admin"))
async def admin_features(message: types.Message):
    await message.answer("Что хотите сделать?", reply_markup=ADMIN_INLINE_KB)


@admin_router.message(StateFilter("*"), Command("отмена"))
@admin_router.message(StateFilter("*"), F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer("Действия отменены", reply_markup=ADMIN_INLINE_KB)


@admin_router.message(Command("назад"))
@admin_router.message(StateFilter("*"), F.text.casefold() == "назад")
async def back_state_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == AddProduct.name:
        await message.answer(
            text="Предыдущего шага нет. Введите название товара или напишите отмена"
        )
        return
    previous = None
    for step in AddProduct.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(
                f"Вы вернулись к предыдущему шагу \n {AddProduct.texts[previous.state]}"
            )
        previous = step


@admin_router.callback_query(StateFilter(None), F.data.startswith("add_product"))
async def change_product(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(AddProduct.name)
    await callback.answer()
    await callback.message.answer(text="Введите название товара")


@admin_router.callback_query(StateFilter(None), F.data.startswith("catalog_products"))
async def change_product(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    products = await ProductsRepoImpl(session=session).get_all()
    await callback.message.answer(text="<strong>Cписок товаров </strong>")
    for idx, product in enumerate(products, start=1):
        await callback.answer()
        await callback.message.answer(
            f"{idx}  {product.name}\n {product.description}",
            reply_markup=get_callback_btns(
                btns={
                    "Удалить товар": f"delete_{product.id}",
                    "Изменить товар": f"update_{product.id}",
                }
            ),
        )


@admin_router.callback_query(StateFilter(None), F.data.startswith("delete_"))
async def delete_product(callback: types.CallbackQuery, session: AsyncSession):
    data = callback.data.split("_")[-1]
    product = await ProductsRepoImpl(session=session).delete(int(data))
    await callback.answer()
    await callback.message.answer(text=f"Товар <strong>{product.name}</strong> удален")


@admin_router.message(F.text == "Изменить товар")
async def change_product(message: types.Message, state: FSMContext):
    await message.answer(
        "ОК, вот список товаров", reply_markup=types.ReplyKeyboardRemove()
    )


@admin_router.message(F.text == "Удалить товар")
async def delete_product(message: types.Message, state: FSMContext):
    await message.answer("Выберите товар(ы) для удаления")


@admin_router.message(AddProduct.name, or_f(F.text, F.text == "далее"))
async def add_name_product(message: types.Message, state: FSMContext):
    if message.text == "далее":
        await state.update_data(name=AddProduct.product_for_update.name)
    else:
        await state.update_data(name=message.text)
    await message.answer(
        text="Введите описание товара", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddProduct.description)


@admin_router.message(AddProduct.name)
async def exc_name_product(message: types.Message, state: FSMContext):
    await message.answer(
        text="Введены не корректные данные. Введите название товара",
        reply_markup=types.ReplyKeyboardRemove(),
    )


@admin_router.message(AddProduct.description, or_f(F.text, F.text == "далее"))
async def add_description_product(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    if message.text == "далее":
        await state.update_data(description=AddProduct.product_for_update.description)
    else:
        await state.update_data(description=message.text)
    cats = await CategoryRepositoryImpl(session=session).get_all()
    await state.set_state(AddProduct.category_id)
    await message.answer(
        text="Выберите категорию", reply_markup=get_reply_keyboard(*cats, size=(2,))
    )


@admin_router.message(AddProduct.description)
async def exc_description_product(message: types.Message, state: FSMContext):
    await message.answer(text="Введеные некорректные данные. Введите описание")


@admin_router.message(AddProduct.category_id, or_f(F.text, F.text == "далее"))
async def add_category_product(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if message.text == "далее":
        await state.update_data(category_id=AddProduct.product_for_update.category_id)
    else:
        try:
            category_id = int(text.split("—", 1)[0].strip())
        except (IndexError, ValueError):
            await message.answer(
                "Неверный формат. Выберите категорию из списка кнопок."
            )
            return
        await state.update_data(category_id=category_id)
    await message.answer(text="Добавте цену", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddProduct.price)


@admin_router.message(AddProduct.category_id)
async def exc_category_product(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    categories = await CategoryRepositoryImpl(session=session).get_all()
    await message.answer(
        text="Введены не корректные данные. Выберите категорию",
        reply_markup=get_reply_keyboard(*categories, size=(2,)),
    )


@admin_router.message(AddProduct.price, or_f(F.text, F.text == "далее"))
async def add_price_product(message: types.Message, state: FSMContext):
    if message.text == "далее":
        ...  # TODO price for product variant
    else:
        await state.update_data(price=message.text)
    await message.answer(text="Добавте изображение")
    await state.set_state(AddProduct.photo)


@admin_router.message(AddProduct.price)
async def exc_price_product(message: types.Message, state: FSMContext):
    await message.answer(text="Введены не корректные данные. Добавте цену")


@admin_router.message(AddProduct.photo, or_f(F.photo, F.text == "далее"))
async def add_photo_product(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text == "далее":
        ...  # TODO photo for product variant
        await state.set_state(AddProduct.update_confirmation)
        await message.answer(
            text=f"Изменить товар?\n\n"
            f"Название: <b>{data["name"]}</b>"
            f"\nОписание: <b>{data["description"]}</b>\n\n"
            "✅ — Да, изменить\n❌ — Отмена",
            reply_markup=get_reply_keyboard("✅ Да", "❌ Отмена"),
        )
    else:
        await state.update_data(photo=message.photo[-1].file_id)
        await message.answer(
            f"Создать товар?\n\nНазвание: <b>{data["name"]}</b>"
            f"\nОписание: <b>{data["description"]}</b>\n\n"
            "✅ — Да, создать\n❌ — Отмена",
            reply_markup=get_reply_keyboard("✅ Да", "❌ Отмена"),
        )
        await state.set_state(AddProduct.confirmation)


@admin_router.message(AddProduct.photo)
async def add_photo_product(message: types.Message, state: FSMContext):
    await message.answer(text="Введены не корректные данные. Добавте фото")


@admin_router.message(AddProduct.confirmation)
async def save_to_db_product(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    # достаём из state остальные поля (name, description и т.д.)
    if message.text == "✅ Да":
        data = await state.get_data()
        name = data["name"]
        description = data["description"]
        category_id = data["category_id"]
        product = ProductSchemaRead(
            name=name,
            description=description,
            category_id=category_id,
        )
        add_product = await ProductsRepoImpl(session=session).add(product)
        await message.answer(
            f"Товар «{add_product.name}» успешно создан в категории {add_product.category_id}.",
            reply_markup=types.ReplyKeyboardRemove(),
        )
        await message.answer(str(data))
    else:
        await message.answer(
            "Создание продукта отменено.", reply_markup=types.ReplyKeyboardRemove()
        )
    AddProduct.product_for_update = None
    await state.clear()
