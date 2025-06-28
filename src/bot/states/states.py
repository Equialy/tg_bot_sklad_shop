from aiogram.fsm.state import StatesGroup, State


class AddProduct(StatesGroup):
    category_id = State()
    name = State()
    description = State()
    waiting_variant = State()
    sku = State()
    price = State()
    stock = State() # колличество
    photo1 = State()
    photo = State()
    confirmation = State()

    texts = {
        'AddProduct:name': 'Введите название заново:',
        'AddProduct:description': 'Введите описание заново:',
        'AddProduct:price': 'Введите стоимость заново:',
        'AddProduct:photo': 'Этот стейт последний, поэтому...',
    }

class AddCategoryProducts(StatesGroup):
    name = State()
    parent_id = State()
    confirmation = State()

