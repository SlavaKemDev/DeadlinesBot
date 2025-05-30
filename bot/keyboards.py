from typing import List

from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from db.models import User, Group, GroupOption, UserSubscription


BTN_UPCOMING_DEADLINES = "📅 Предстоящие дедлайны"
BTN_MY_SUBSCRIPTIONS = "📝 Мои подписки"
BTN_ADMIN_PANEL = "🔧 Админ-панель"


def get_menu_keyboard(user: User) -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text=BTN_UPCOMING_DEADLINES)],
        [KeyboardButton(text=BTN_MY_SUBSCRIPTIONS)],
    ]

    if user.is_admin:
        buttons.append([KeyboardButton(text=BTN_ADMIN_PANEL)])

    menu_keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выберите действие"
    )

    return menu_keyboard


def get_deadlines_list_keyboard(by_group: bool = True) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(
            text="Сгруппировать по предметам" if not by_group else "Не группировать",
            callback_data=f"deadlines_{int(not by_group)}"
        )
    ]

    deadlines_keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
    return deadlines_keyboard


def get_subscriptions_keyboard(my_subscriptions: List[GroupOption], all_groups: List[Group]):
    buttons = []

    my_ids = {opt.id for opt in my_subscriptions}

    for group in all_groups:
        layer = []
        for option in sorted(group.options, key=lambda x: x.name):
            layer.append(
                InlineKeyboardButton(
                    text=f"{'✅ ' if option.id in my_ids else ''}{group.name} {option.name}",
                    callback_data=f"option_{option.id}"
                )
            )

        buttons.append(layer)

    subscriptions_keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return subscriptions_keyboard
