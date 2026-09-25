"""Fill the database with demo products for development.

Usage: python manage.py seed_demo_data [--reset]
"""

from django.core.files.base import ContentFile
from django.core.files import File
from django.conf import settings
from django.core.management.base import BaseCommand

from apps.catalog.models import Banner, Brand, Category, Color, Product, ProductImage, Size
from apps.catalog.placeholders import make_product_placeholder, make_promo_banner, make_hero_banner

LEGACY_IMAGES = settings.BASE_DIR / "legacy_frontend_reference" / "images"

CATEGORY_DATA = [
    {"name": "لوازم آرایشی", "icon_class": "ri-paint-brush-line"},
    {"name": "پوشاک", "icon_class": "ri-t-shirt-line"},
    {"name": "اکسسوری", "icon_class": "ri-vip-diamond-line"},
]

COLOR_DATA = [
    ("مشکی", "#1a1a1a"),
    ("سفید", "#f5f5f5"),
    ("قرمز", "#ca1250"),
    ("آبی", "#1f5fae"),
    ("طلایی", "#c9a227"),
    ("نقره‌ای", "#9e9e9e"),
    ("صورتی", "#e75a97"),
    ("سبز", "#2e7d32"),
]

B = Product.Badge
# (name, price, old_price, badge, brand, color, featured)
PRODUCTS_BY_CATEGORY = {
    "لوازم آرایشی": [
        ("رژ لب مایع مات برند مک", 299000, 350000, B.BESTSELLER, "مک", "قرمز", True),
        ("پالت سایه چشم ۱۲ رنگ هودا بیوتی", 450000, 520000, B.NEW, "هودا بیوتی", None, True),
        ("کرم پودر فول کاور لورال پاریس", 180000, 220000, B.SPECIAL_DISCOUNT, "لورال پاریس", None, False),
        ("ریمل حجم‌دهنده میبلین", 160000, 190000, B.NONE, "میبلین", "مشکی", False),
        ("خط چشم مایع ضدآب نیکس", 145000, 190000, B.SPECIAL_DISCOUNT, "نیکس", "مشکی", False),
        ("کرم مرطوب‌کننده نیوآ", 95000, None, B.NEW, "نیوآ", None, False),
        ("رژگونه دو رنگ ام‌یو‌اِی", 210000, 260000, B.NONE, None, "صورتی", False),
        ("کانسیلر روشن‌کننده مک", 320000, None, B.BESTSELLER, "مک", None, True),
        ("ماسک صورت خاک رس", 85000, 100000, B.SPECIAL_DISCOUNT, None, None, False),
        ("کرم ضد آفتاب SPF50", 240000, 290000, B.NEW, "نیوآ", None, False),
        ("لاک ناخن براق", 65000, None, B.NONE, None, "قرمز", False),
        ("برس آرایشی ست ۸ عددی", 380000, 450000, B.BESTSELLER, None, "صورتی", False),
    ],
    "پوشاک": [
        ("مانتو اسپرت زنانه", 620000, None, B.NEW, None, "مشکی", True),
        ("شلوار جین کلاسیک", 540000, 650000, B.SPECIAL_DISCOUNT, None, "آبی", False),
        ("تیشرت نخی مردانه", 220000, None, B.NONE, None, "سفید", False),
        ("کاپشن زمستانی", 980000, 1200000, B.BESTSELLER, None, "مشکی", True),
        ("پیراهن مردانه آستین بلند", 450000, 520000, B.NONE, None, "آبی", False),
        ("سویشرت هودی یونیسکس", 390000, None, B.NEW, None, "سبز", False),
        ("شومیز زنانه طرح‌دار", 360000, 420000, B.SPECIAL_DISCOUNT, None, "صورتی", False),
        ("شلوار راحتی نخی", 280000, None, B.NONE, None, "مشکی", False),
        ("پولوشرت مردانه", 320000, 380000, B.BESTSELLER, None, "سفید", False),
        ("دامن بلند مجلسی", 540000, None, B.NEW, None, "مشکی", False),
        ("تاپ ورزشی زنانه", 190000, 240000, B.SPECIAL_DISCOUNT, None, "صورتی", False),
        ("کت تک رسمی مردانه", 1450000, 1700000, B.NONE, None, "مشکی", False),
    ],
    "اکسسوری": [
        ("کیف دستی چرم زنانه", 1200000, None, B.BESTSELLER, None, "مشکی", True),
        ("ساعت مچی کلاسیک", 3200000, 3600000, B.SPECIAL_DISCOUNT, None, "طلایی", True),
        ("انگشتر نقره طرح‌دار", 450000, None, B.NEW, None, "نقره‌ای", False),
        ("عینک آفتابی پلاریزه", 380000, 460000, B.NONE, None, "مشکی", False),
        ("گردنبند طلا روکش", 680000, 790000, B.BESTSELLER, None, "طلایی", False),
        ("کمربند چرم مردانه", 290000, None, B.NONE, None, "مشکی", False),
        ("کلاه بافت زمستانی", 150000, 190000, B.SPECIAL_DISCOUNT, None, "سبز", False),
        ("دستبند چرم و استیل", 220000, None, B.NEW, None, "مشکی", False),
        ("شال نخی زنانه", 180000, 220000, B.NONE, None, "صورتی", False),
        ("کیف پول چرم", 340000, 400000, B.BESTSELLER, None, "مشکی", False),
        ("ساعت هوشمند اسپرت", 2400000, 2900000, B.NEW, None, "مشکی", True),
        ("گوشواره آویز نقره", 260000, None, B.NONE, None, "نقره‌ای", False),
    ],
}


class Command(BaseCommand):
    help = "Seed demo categories, brands, colors, products (with generated images) and banners."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset", action="store_true", help="Delete existing products/brands/colors before seeding."
        )

    def handle(self, *args, **options):
        if options["reset"]:
            ProductImage.objects.all().delete()
            Product.objects.all().delete()
            Brand.objects.all().delete()
            Color.objects.all().delete()
            self.stdout.write(self.style.WARNING("Existing catalog cleared."))

        colors = self._seed_colors()
        clothing_sizes = self._seed_sizes()
        image_index = 0

        for cat_data in CATEGORY_DATA:
            category, _ = Category.objects.get_or_create(
                name=cat_data["name"], defaults={"icon_class": cat_data["icon_class"]}
            )

            for name, price, old_price, badge, brand_name, color_name, featured in PRODUCTS_BY_CATEGORY[cat_data["name"]]:
                brand = Brand.objects.get_or_create(name=brand_name)[0] if brand_name else None

                product, created = Product.objects.get_or_create(
                    name=name,
                    defaults={
                        "category": category,
                        "brand": brand,
                        "color": colors.get(color_name),
                        "description": (
                            f"{name} — یکی از محصولات پرطرفدار فروشگاه K2 با کیفیت تضمین‌شده، "
                            "اصالت کالا و ارسال سریع به سراسر کشور. مناسب برای استفاده روزمره و هدیه."
                        ),
                        "price": price,
                        "old_price": old_price,
                        "stock": 25,
                        "badge": badge,
                        "is_featured": featured,
                    },
                )

                if not product.images.exists():
                    png = make_product_placeholder(name, index=image_index)
                    ProductImage.objects.create(
                        product=product,
                        image=ContentFile(png, name=f"{product.slug}.png"),
                        alt_text=name,
                    )
                    self.stdout.write(f"{'Created' if created else 'Imaged'}: {name}")
                image_index += 1

                if cat_data["name"] == "پوشاک" and not product.sizes.exists():
                    product.sizes.set(clothing_sizes)

                if not product.colors.exists():
                    if cat_data["name"] == "پوشاک":
                        chosen = [colors.get(n) for n in ["مشکی", "سفید", "قرمز", "آبی", "سبز"]]
                        product.colors.set([c for c in chosen if c])
                    elif product.color:
                        product.colors.add(product.color)

        self._seed_banners()
        self.stdout.write(self.style.SUCCESS("Demo data seeding complete."))

    def _seed_colors(self):
        colors = {}
        for name, hex_code in COLOR_DATA:
            colors[name] = Color.objects.get_or_create(name=name, defaults={"hex_code": hex_code})[0]
        return colors

    def _seed_sizes(self):
        sizes = []
        for order, name in enumerate(["S", "M", "L", "XL", "XXL", "فری‌سایز"]):
            sizes.append(Size.objects.get_or_create(name=name, defaults={"order": order})[0])
        # S-XL for clothing
        return sizes[:4]

    def _seed_banners(self):
        if Banner.objects.exists():
            return

        # hero slides
        hero_slides = [
            ("جشنواره لوازم آرایشی", "تا ۵۰٪ تخفیف روی برندهای اصل", "لوازم-آرایشی"),
            ("کالکشن جدید پوشاک", "استایل هر فصل را با ما بساز", "پوشاک"),
            ("اکسسوری‌های خاص", "تکمیل‌کننده‌ی ست شما", "اکسسوری"),
        ]
        for index, (title, subtitle, slug) in enumerate(hero_slides):
            png = make_hero_banner(title, subtitle, index=index)
            Banner.objects.create(
                title=title,
                image=ContentFile(png, name=f"hero-{index}.png"),
                link_url=f"/c/{slug}/",
                placement=Banner.Placement.HERO,
                order=index,
            )

        # promo banners
        promos = [
            ("لوازم آرایشی", "جدیدترین برندهای روز", "لوازم-آرایشی"),
            ("پوشاک", "استایل هر فصل", "پوشاک"),
            ("اکسسوری", "تکمیل‌کننده‌ی ست شما", "اکسسوری"),
        ]
        for index, (title, subtitle, slug) in enumerate(promos):
            png = make_promo_banner(title, subtitle, index=index)
            Banner.objects.create(
                title=title,
                image=ContentFile(png, name=f"promo-{index}.png"),
                link_url=f"/c/{slug}/",
                placement=Banner.Placement.PROMO,
                order=index,
            )
