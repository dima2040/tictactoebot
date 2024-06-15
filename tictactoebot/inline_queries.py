from aiogram import Router, types

from .keyboards import make_invite_kb


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
            ),
            reply_markup=make_invite_kb(
                inline_query.from_user.id,
                'en'
            )
        )
    ]

    await inline_query.answer(
        results, cache_time=1,
        switch_pm_parameter='must_click'
    )