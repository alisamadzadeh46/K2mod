"""Persian digits, prices and jalali dates."""

import jdatetime
from django import template
from django.utils import timezone as dj_timezone

register = template.Library()

_DIGIT_MAP = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")

_JMONTHS = [
    "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند",
]


@register.filter
def persian_digits(value):
    return str(value).translate(_DIGIT_MAP)


@register.filter
def toman(value):
    """1234567 -> ۱٬۲۳۴٬۵۶۷"""
    try:
        amount = int(value)
    except (TypeError, ValueError):
        return value
    grouped = f"{amount:,}".replace(",", "٬")
    return grouped.translate(_DIGIT_MAP)


def _to_local(value):
    if dj_timezone.is_aware(value):
        return dj_timezone.localtime(value)
    return value


@register.filter
def jalali(value):
    """e.g. ۱۴ مرداد ۱۴۰۴"""
    if not value:
        return ""
    value = _to_local(value)
    j = jdatetime.date.fromgregorian(date=value.date() if hasattr(value, "date") else value)
    return f"{j.day} {_JMONTHS[j.month - 1]} {j.year}".translate(_DIGIT_MAP)


@register.filter
def jalali_datetime(value):
    """e.g. ۱۴ مرداد ۱۴۰۴ - ۱۸:۰۵"""
    if not value:
        return ""
    local = _to_local(value)
    jd = jalali(value)
    return f"{jd} - {local.strftime('%H:%M')}".translate(_DIGIT_MAP)
