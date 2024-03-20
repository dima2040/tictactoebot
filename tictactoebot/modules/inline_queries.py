from aiogram import Bot, Router, types
import os

#bot = Bot(token=os.environ.get("TTT_API_TOKEN"))
router = Router()

@router.inline_query()
async def action_list(inline_query: types.InlineQuery):
    results = [
        types.InlineQueryResultArticle(
            id = 'play',
            title='Сыграть в игру!',
            description='Вы предлагаете игроку сыграть в игру',
            input_message_content= types.InputTextMessageContent(
                message_text='Зову тебя поиграть!'
            )
        )
    ]



    await inline_query.answer(
        results, cache_time=1,
        switch_pm_parameter='must_click'
    )