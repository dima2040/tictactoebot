from aiogram.filters.callback_data import CallbackData


class FieldFilter(CallbackData, prefix="fd"):
    index: int
    status: str
    board_id:int

class PickFilter(CallbackData, prefix="pick"):
    value: str

class LanguageFilter(CallbackData, prefix = "lang"):
    code: str


class DifficultyFilter(CallbackData, prefix = "difficulty"):
    level: str

class MenuFilter(CallbackData, prefix='menu') :
    action: str
class InviteFilter(CallbackData, prefix='iv'):
    author: int
