import os

import phonenumbers
import telebot
from phonenumbers import carrier, geocoder, timezone
from phonenumbers.phonenumberutil import NumberParseException


TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("Set BOT_TOKEN environment variable before starting the bot.")

bot = telebot.TeleBot(TOKEN, parse_mode=None)


def parse_phone_number(text: str):
    value = text.strip()

    if value.startswith("8") and len(value) == 11:
        value = "+7" + value[1:]

    default_region = None if value.startswith("+") else "RU"
    return phonenumbers.parse(value, default_region)


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    answer = (
        "Привет! Отправь номер телефона, а я проверю его формат и покажу "
        "открытую справочную информацию: регион, оператора и часовой пояс.\n\n"
        "Пример: +79991234567"
    )
    bot.send_message(message.chat.id, answer)


@bot.message_handler(content_types=["text"])
def check_number(message):
    try:
        phone_number = parse_phone_number(message.text)
    except NumberParseException:
        bot.send_message(
            message.chat.id,
            "Не получилось распознать номер. Отправь его в формате +79991234567.",
        )
        return

    is_valid = phonenumbers.is_valid_number(phone_number)
    is_possible = phonenumbers.is_possible_number(phone_number)
    formatted_number = phonenumbers.format_number(
        phone_number,
        phonenumbers.PhoneNumberFormat.INTERNATIONAL,
    )

    operator_name = carrier.name_for_number(phone_number, "ru") or "не найден"
    region_name = geocoder.description_for_number(phone_number, "ru") or "не найден"
    time_zones = timezone.time_zones_for_number(phone_number)
    time_zones_text = ", ".join(time_zones) if time_zones else "не найден"

    answer = (
        f"Номер: {formatted_number}\n"
        f"Возможный формат: {'да' if is_possible else 'нет'}\n"
        f"Валидный номер: {'да' if is_valid else 'нет'}\n"
        f"Регион: {region_name}\n"
        f"Оператор: {operator_name}\n"
        f"Часовой пояс: {time_zones_text}"
    )
    bot.send_message(message.chat.id, answer)


if __name__ == "__main__":
    bot.infinity_polling(skip_pending=True)
