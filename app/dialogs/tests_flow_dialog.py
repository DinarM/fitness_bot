from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Format, Const
from app.dialogs.common import MAIN_MENU_BUTTON
from app.getters.test_flow_getters import final_review_getter, single_choice_type_getter, start_test_getter, question_input_getter
from app.handlers.test_flow_handlers import check_numeric_type, error_numeric_type, has_selected_items, multi_answer_handler, next_question, no_text, save_test_results, single_answer_handler, start_test
from app.dialogs.states import TestsSG
from aiogram.enums import ContentType
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.kbd import Multiselect, Radio, Group

start_test_window = Window(
        Format('<b>{name}!</b>\n'),
        Format('<b>{description}!</b>\n'),
        Format('<b>Займет времени: {estimated_duration}!</b>\n', when=lambda data, *_: data.get('estimated_duration') is not None),
        Button(Const('Начать тестирование ▶️'), id='b_next', on_click=start_test),
        MAIN_MENU_BUTTON,
        getter=start_test_getter,
        state=TestsSG.START_WINDOW,
        parse_mode="HTML",
    )
text_type_dialog = Window(
        Format('{question_number}. {question_text}'),
        Format('\n<i>(✍️ Введите текстовый ответ ниже)</i>'),
        TextInput(
            id='text_input',
            on_success=single_answer_handler,
        ),
        MessageInput(
            func=no_text,
            content_types=ContentType.ANY
        ),
        getter=question_input_getter,
        state=TestsSG.TEXT_TYPE_WINDOW,
        parse_mode="HTML",
    )
single_choice_type_dialog = Window(
        Format('{question_number}. {question_text}'),
        Format('\n<i>(🔘 Выберите один вариант)</i>'),
        Radio(
            # Format("⚪️ {item[name]}"),
            checked_text=Format('🔘 {item[name]}'),
            unchecked_text=Format('⚪️ {item[name]}'),
            id="checkbox",
            item_id_getter=lambda item: item["id"],
            items="possible_answers",
            on_click=single_answer_handler,
        ),
        Button(
            Const("⏭ Следующий вопрос"),
            id="next_question",
            on_click=next_question,
            when=has_selected_items
        ),
        MAIN_MENU_BUTTON,
        getter=single_choice_type_getter,
        state=TestsSG.SINGLE_CHOICE_TYPE_WINDOW,
        parse_mode="HTML",
        )
multiple_choice_type_dialog = Window(
    Format('{question_number}. {question_text}'),
    Format('\n<i>([✓] Выберите несколько вариантов)</i>'),
    Multiselect(
        checked_text=Format('[✓] {item[name]}'),
        unchecked_text=Format('[  ] {item[name]}'),
        id="multi_select",
        item_id_getter=lambda item: item["id"],
        items="possible_answers",
        on_click=multi_answer_handler,
    ),
    Button(
        Const("⏭ Следующий вопрос"),
        id="next_question",
        on_click=next_question,
        when=has_selected_items
    ),
    MAIN_MENU_BUTTON,
    getter=single_choice_type_getter,
    state=TestsSG.MULTIPLE_CHOICE_TYPE_WINDOW,
    parse_mode="HTML",
    )
numeric_type_dialog = Window(
    Format('{question_number}. {question_text}'),
    Format('\n<i>(🔢 Введите число)</i>'),
    TextInput(
        id='numeric_input',
        type_factory=check_numeric_type,
        on_success=single_answer_handler,
        on_error=error_numeric_type
    ),
    MessageInput(
        func=no_text,
        content_types=ContentType.ANY
    ),
    getter=question_input_getter,
    state=TestsSG.NUMERIC_TYPE_WINDOW,
    parse_mode="HTML",
)
rating_type_dialog = Window(
    Format('{question_number}. {question_text}'),
    Format('\n<i>(⭐ Оцените по шкале от 1 до 10)</i>'),
    Group(
        Radio(
            checked_text=Format('🔘 {item}'),
            unchecked_text=Format('⚪️ {item}'),
            id="rating_radio",
            item_id_getter=lambda item: str(item),
            items=[i for i in range(1, 11)],
            on_click=single_answer_handler,
        ),
    width=5
    ),
    Button(
        Const("⏭ Следующий вопрос"),
        id="next_question",
        on_click=next_question,
        when=has_selected_items
    ),
    MAIN_MENU_BUTTON,
    getter=question_input_getter,
    state=TestsSG.RATING_TYPE_WINDOW,
    parse_mode="HTML",
)
final_review_window = Window(
    Format('<b>Проверьте ваши ответы:</b>\n\n'),
    Format('{formatted_text}'),
    Button(
        Const('✅ Сохранить результаты'),
        id='save_results',
        on_click=save_test_results
    ),
    Button(
        Const('🔄 Начать заново'),
        id='restart_test',
        on_click=start_test
    ),
    MAIN_MENU_BUTTON,
    getter=final_review_getter,
    state=TestsSG.FINAL_REVIEW_WINDOW,
    parse_mode='HTML'
)


tests_dialog = Dialog(
    start_test_window,
    text_type_dialog,
    single_choice_type_dialog,
    multiple_choice_type_dialog,
    numeric_type_dialog,
    rating_type_dialog,
    final_review_window,
)