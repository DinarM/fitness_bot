from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Format, Const
from app.getters.test_flow_getters import single_choice_type_getter, start_test_getter, text_type_getter
from app.handlers.test_flow_handlers import answer_handler, no_text, start_test
from app.dialogs.states import TestsSG
from aiogram.enums import ContentType
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.kbd import Select


start_test_window = Window(
        Format('<b>{name}!</b>\n'),
        Format('<b>{description}!</b>\n'),
        Format('<b>Займет времени: {estimated_duration}!</b>\n', when=lambda data, *_: data.get('estimated_duration') is not None),
        Button(Const('Начать тестирование ▶️'), id='b_next', on_click=start_test),
        getter=start_test_getter,
        state=TestsSG.START_WINDOW,
        parse_mode="HTML",
    )
text_type_dialog = Window(
        Format('{question_number}. {question_text}'),
        TextInput(
            id='text_input',
            on_success=answer_handler
        ),
        MessageInput(
            func=no_text,
            content_types=ContentType.ANY
        ),
        getter=text_type_getter,
        state=TestsSG.TEXT_TYPE_WINDOW,
    )
single_choice_type_dialog = Window(
        Format('{question_number}. {question_text}'),
        Select(
            Format("🔹 {item[name]}"),
            id="answer_select",
            item_id_getter=lambda item: item["id"],
            items="possible_answers",
            on_click=answer_handler,
        ),
        getter=single_choice_type_getter,
        state=TestsSG.SINGLE_CHOICE_TYPE_WINDOW,
        )


tests_dialog = Dialog(
    start_test_window,
    text_type_dialog,
    single_choice_type_dialog,
)