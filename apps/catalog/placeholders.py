"""Placeholder images (products, slides, banners) with persian text."""

from io import BytesIO

import arabic_reshaper
from bidi.algorithm import get_display
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont, features

FONT_PATH = settings.BASE_DIR / "static" / "fonts" / "Vazirmatn-VariableFont_wght.ttf"

# pillow with raqm handles rtl shaping itself, otherwise we do it
_HAS_RAQM = features.check("raqm")

# (top, bottom) gradient colors
PALETTES = [
    ((202, 18, 80), (138, 10, 54)),
    ((156, 39, 176), (74, 20, 110)),
    ((60, 75, 109), (32, 42, 64)),
    ((0, 150, 136), (0, 96, 88)),
    ((216, 67, 21), (140, 40, 10)),
    ((30, 95, 174), (18, 58, 110)),
    ((194, 124, 14), (140, 88, 8)),
    ((46, 125, 50), (24, 78, 32)),
]

SIZE = 800


def _shape(text):
    if _HAS_RAQM:
        return text
    return get_display(arabic_reshaper.reshape(text))


def _vertical_gradient(top, bottom):
    base = Image.new("RGB", (1, SIZE))
    for y in range(SIZE):
        ratio = y / (SIZE - 1)
        base.putpixel(
            (0, y),
            (
                round(top[0] + (bottom[0] - top[0]) * ratio),
                round(top[1] + (bottom[1] - top[1]) * ratio),
                round(top[2] + (bottom[2] - top[2]) * ratio),
            ),
        )
    return base.resize((SIZE, SIZE))


def _wrap(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textlength(_shape(candidate), font=font) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def make_product_placeholder(name, index=0):
    palette = PALETTES[index % len(PALETTES)]
    image = _vertical_gradient(*palette)
    draw = ImageDraw.Draw(image)

    draw.ellipse([SIZE - 220, -120, SIZE + 120, 220], fill=(255, 255, 255, 30))

    title_font = ImageFont.truetype(str(FONT_PATH), 52)
    mark_font = ImageFont.truetype(str(FONT_PATH), 30)

    lines = _wrap(draw, name, title_font, max_width=SIZE - 120)
    line_height = 70
    total_height = line_height * len(lines)
    y = (SIZE - total_height) / 2

    for line in lines:
        shaped = _shape(line)
        width = draw.textlength(shaped, font=title_font)
        draw.text(((SIZE - width) / 2, y), shaped, font=title_font, fill="#ffffff")
        y += line_height

    mark = "k2mod"
    shaped_mark = _shape(mark)
    mark_width = draw.textlength(shaped_mark, font=mark_font)
    draw.text(((SIZE - mark_width) / 2, SIZE - 90), shaped_mark, font=mark_font, fill=(255, 255, 255, 200))

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _horizontal_gradient(width, height, left, right):
    base = Image.new("RGB", (width, 1))
    for x in range(width):
        ratio = x / (width - 1)
        base.putpixel(
            (x, 0),
            (
                round(left[0] + (right[0] - left[0]) * ratio),
                round(left[1] + (right[1] - left[1]) * ratio),
                round(left[2] + (right[2] - left[2]) * ratio),
            ),
        )
    return base.resize((width, height))


def make_hero_banner(title, subtitle, index=0, width=1600, height=520):
    palette = PALETTES[index % len(PALETTES)]
    image = _horizontal_gradient(width, height, palette[1], palette[0]).convert("RGBA")

    # circles on the left, text is on the right
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    odraw.ellipse([-220, -240, 360, 340], fill=(255, 255, 255, 24))
    odraw.ellipse([120, height - 220, 520, height + 220], fill=(255, 255, 255, 18))
    odraw.ellipse([width - 460, height - 320, width - 60, height + 80], fill=(255, 255, 255, 14))
    image = Image.alpha_composite(image, overlay).convert("RGB")
    draw = ImageDraw.Draw(image)

    title_font = ImageFont.truetype(str(FONT_PATH), 82)
    sub_font = ImageFont.truetype(str(FONT_PATH), 38)
    cta_font = ImageFont.truetype(str(FONT_PATH), 32)

    margin = 90
    title_shaped = _shape(title)
    title_w = draw.textlength(title_shaped, font=title_font)
    draw.text((width - margin - title_w, height / 2 - 110), title_shaped, font=title_font, fill="#ffffff")

    if subtitle:
        sub_shaped = _shape(subtitle)
        sub_w = draw.textlength(sub_shaped, font=sub_font)
        draw.text((width - margin - sub_w, height / 2 - 5), sub_shaped, font=sub_font, fill=(255, 255, 255, 235))

    cta = _shape("مشاهده محصولات")
    cta_w = draw.textlength(cta, font=cta_font)
    pill_w, pill_h = cta_w + 72, 68
    pill_x = width - margin - pill_w
    pill_y = height / 2 + 70
    draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=34, fill="#ffffff")
    draw.text((pill_x + 36, pill_y + 15), cta, font=cta_font, fill=palette[1])

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def make_promo_banner(title, subtitle, index=0, width=900, height=420):
    palette = PALETTES[index % len(PALETTES)]
    image = _horizontal_gradient(width, height, palette[1], palette[0]).convert("RGBA")

    # circles on a separate RGBA layer so alpha works
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    odraw.ellipse([-150, -160, 230, 220], fill=(255, 255, 255, 26))
    odraw.ellipse([60, height - 150, 360, height + 150], fill=(255, 255, 255, 20))
    image = Image.alpha_composite(image, overlay).convert("RGB")
    draw = ImageDraw.Draw(image)

    title_font = ImageFont.truetype(str(FONT_PATH), 56)
    sub_font = ImageFont.truetype(str(FONT_PATH), 28)
    cta_font = ImageFont.truetype(str(FONT_PATH), 26)

    margin = 60
    title_shaped = _shape(title)
    title_w = draw.textlength(title_shaped, font=title_font)
    draw.text((width - margin - title_w, height / 2 - 70), title_shaped, font=title_font, fill="#ffffff")

    if subtitle:
        sub_shaped = _shape(subtitle)
        sub_w = draw.textlength(sub_shaped, font=sub_font)
        draw.text((width - margin - sub_w, height / 2 + 5), sub_shaped, font=sub_font, fill=(255, 255, 255, 230))

    # button
    cta = _shape("مشاهده محصولات")
    cta_w = draw.textlength(cta, font=cta_font)
    pill_w, pill_h = cta_w + 56, 56
    pill_x = width - margin - pill_w
    pill_y = height / 2 + 60
    draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=28, fill="#ffffff")
    draw.text((pill_x + 28, pill_y + 12), cta, font=cta_font, fill=palette[1])

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
