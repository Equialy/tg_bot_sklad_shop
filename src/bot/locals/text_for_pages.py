from aiogram.utils.formatting import Bold, as_list, as_marked_section


description_pages = {
    "main": "Добро пожаловать!",
    "about": "Shop Sklad.\n",
    "payment": as_marked_section(
        Bold("Варианты оплаты:"),
        "Картой в боте",
        "При получении карта/кеш",
        marker="✅ ",
    ).as_html(),
    "delivery": as_list(
        as_marked_section(
            Bold("Варианты доставки:"),
            "Доставка",
            "Самовывоз",
            marker="✅ ",
        ),
    ).as_html(),
    "catalog": "Каталог:",
    "cart": "В корзине ничего нет!",
}
