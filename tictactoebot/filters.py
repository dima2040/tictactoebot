from aiogram.filters.callback_data import CallbackData


class ButtonFilter(CallbackData, prefix="btn"):
    index: int
    status: str


class LanguageFilter(CallbackData, prefix = "lang"):
    code: str


class DifficultyFilter(CallbackData, prefix = "difficulty"):
    level: str

class MenuFilter(CallbackData, prefix='menu') :
    action: str
