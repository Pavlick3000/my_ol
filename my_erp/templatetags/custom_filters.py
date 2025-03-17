import re

from django import template

register = template.Library()

@register.filter
def dict_get(dictionary, key):
    return dictionary.get(key, "Не найдено")

@register.filter
def format_qnt(value):
    """Фильтр для форматирования qnt как в JavaScript с разделением на тысячи"""
    if value is None:
        return "0"
    try:
        value = float(value)
        # Форматируем число до 3 знаков после запятой.
        formatted = f"{value:.3f}".rstrip("0").rstrip(".")  # Убираем лишние нули

        # Разделяем целую часть и дробную
        integer_part, *decimal_part = formatted.split(".")

        # Разделяем целую часть на тысячи
        integer_part = re.sub(r"(?<=\d)(?=(\d{3})+(\.|\b))", r" ", integer_part)

        # Если дробная часть существует, добавляем её обратно
        return f"{integer_part}{'.' + decimal_part[0] if decimal_part else ''}"
    except (ValueError, TypeError):
        return "0"