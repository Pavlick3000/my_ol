from django import template

register = template.Library()

@register.filter
def dict_get(dictionary, key):
    return dictionary.get(key, "Не найдено")

@register.filter
def format_qnt(value):
    """Фильтр для форматирования qnt как в JavaScript"""
    if value is None:
        return "0"
    try:
        value = float(value)
        formatted = f"{value:.3f}".rstrip("0").rstrip(".")  # Убираем лишние нули
        return formatted
    except (ValueError, TypeError):
        return "0"