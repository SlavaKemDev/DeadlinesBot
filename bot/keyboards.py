from typing import List

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from db.models import User, Group, GroupOption, Deadline

from . import consts


def get_menu_keyboard(user: User) -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text=consts.BTN_UPCOMING_DEADLINES)],
        [KeyboardButton(text=consts.BTN_MY_SUBSCRIPTIONS)],
    ]

    if user.is_admin:
        buttons.append([KeyboardButton(text=consts.BTN_ADMIN_PANEL)])

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


def get_admin_keyboard() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text=consts.BTN_ADMIN_STATS)],
        [KeyboardButton(text=consts.BTN_ADMIN_USERS)],
        [KeyboardButton(text=consts.BTN_ADMIN_GROUPS)],
        [KeyboardButton(text=consts.BTN_ADMIN_EXIT)],
    ]

    admin_keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выберите действие"
    )

    return admin_keyboard


def get_admin_groups(groups: List[Group]) -> InlineKeyboardMarkup:
    buttons = []

    for group in groups:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=group.name,
                    callback_data=f"group_{group.id}"
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text=consts.BTN_ADD_GROUP,
                callback_data=f"add_group"
            )
        ]
    )

    admin_groups_keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return admin_groups_keyboard


def get_admin_group_options(group: Group) -> InlineKeyboardMarkup:
    buttons = []

    for option in group.options:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{option.name or 'Без имени'}",
                    callback_data=f"option_{option.id}"
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text="➕ Добавить опцию",
                callback_data=f"add_option_{group.id}"
            )
        ]
    )

    admin_group_options_keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return admin_group_options_keyboard


def get_admin_option_keyboard(option: GroupOption, deadlines: List[Deadline]) -> InlineKeyboardMarkup:
    buttons = []

    for deadline in deadlines:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{deadline.name} ({deadline.date.strftime('%d.%m.%Y %H:%M')})",
                    callback_data=f"deadline_{deadline.id}"
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text="➕ Добавить дедлайн",
                callback_data=f"add_deadline_{option.id}"
            )
        ]
    )
    buttons.append(
        [
            InlineKeyboardButton(
                text="💬 Изменить канал",
                callback_data=f"change_channel_{option.id}"
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_admin_deadline_keyboard(deadline: Deadline) -> InlineKeyboardMarkup:
    buttons = [

        [
            InlineKeyboardButton(
                text="Изменить название",
                callback_data=f"change_name_deadline_{deadline.id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="Изменить дату",
                callback_data=f"change_date_deadline_{deadline.id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="Удалить",
                callback_data=f"delete_deadline_{deadline.id}"
            )
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
