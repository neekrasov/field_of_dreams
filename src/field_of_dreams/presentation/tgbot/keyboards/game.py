def choice_letter_or_word() -> dict:
    return {
        "inline_keyboard": [
            [
                {"text": "Букву", "callback_data": "letter"},
                {"text": "Слово", "callback_data": "word"},
            ],
            [{"text": "Пропустить ход", "callback_data": "skip"}],
        ]
    }


def only_word_choice() -> dict:
    return {
        "inline_keyboard": [
            [
                {"text": "Слово", "callback_data": "word"},
            ],
            [{"text": "Пропустить ход", "callback_data": "skip"}],
        ]
    }
