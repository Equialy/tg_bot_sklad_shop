from aiogram.utils.formatting import Bold, as_list, as_marked_section


desctiption_pages = {
    "main": "Добро пожаловать!",
    "about": "Shop Sklad.\n",
    "payment": as_marked_section(
        Bold("Варианты оплаты:"),
        "Картой в боте",
        "При получении карта/кеш",
        "В заведении",
        marker="✅ ",
    ).as_html(),
    "shipping": as_list(
        as_marked_section(
            Bold("Варианты доставки:"),
            "Курьер",
            "Самовывоз",
            marker="✅ ",
        ),
        as_marked_section(Bold("Нельзя:"), "Почта", "Голуби", marker="❌ "),
        sep="\n----------------------\n",
    ).as_html(),
    "catalog": "Категории:",
    "cart": "В корзине ничего нет!",
}
