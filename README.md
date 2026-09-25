# k2mod

<p align="center">
  <img src="docs/screenshots/home.png" alt="k2mod home page" width="900">
</p>

<p align="center">
  <a href="#english">English</a> · <a href="#فارسی">فارسی</a>
</p>

---

## English

k2mod is an online store for gifts, cosmetics, clothing and accessories, built with Django. The site is in Persian (RTL), prices are in Toman and dates are Jalali.

**Live demo (home page only):** https://alisamadzadeh46.github.io/K2mod/

### Features

**Store**
- Sign up and log in with a mobile number, password reset by email
- Categories and subcategories, brands, colors and sizes
- Product listing with filters (price range, color, size, in stock) and sorting
- Product page with image gallery, color and size picker
- Search
- Wishlist
- Product comments with approval
- Guest cart
- Checkout with discount codes and shipping cost (free shipping above a set amount)
- Order history, order tracking code and saved addresses in the user account
- Responsive

**Custom admin panel**
- Dashboard with sales, orders, new users and recent activity
- Manage products (text editor, multiple images, SEO fields)
- Manage categories, brands and colors
- Orders: change status, set carrier and tracking code
- Discount codes (percentage or fixed amount, with a Jalali date picker)
- Shipping settings
- Comment moderation and replies
- User management (activate/deactivate, staff access)
- Sales reports

**Security**
- Login attempt limiting with django-axes
- Argon2 password hashing
- Admin URLs are set in `.env`

### Tech stack

- **Backend:** Python, Django 6
- **Database:** PostgreSQL
- **Frontend:** HTML, CSS, JavaScript (no frontend framework), Django templates
- **Icons & font:** Remix Icon, Vazirmatn
- **Other packages:** django-environ, django-axes, argon2-cffi, Pillow, jdatetime, arabic-reshaper, python-bidi
- **Deployment:** Gunicorn

### Running it locally

Requirements: Python 3.12+ and PostgreSQL.

```bash
git clone https://github.com/alisamadzadeh46/k2mod.git
cd k2mod

python -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a PostgreSQL database and set up your `.env`:

```bash
cp .env.example .env            # on Windows: copy .env.example .env
```

Fill in `SECRET_KEY`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` and `DJANGO_ADMIN_URL_PREFIX`.

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000. The admin panel is at `/panel-control/` (can be changed with `DASHBOARD_URL_PREFIX`).

To add some sample products:

```bash
python manage.py seed_demo_data
```

### Screenshots

| Home | Product list |
|---|---|
| ![Home](docs/screenshots/home.png) | ![Product list](docs/screenshots/product-list.png) |

| Product page | Checkout |
|---|---|
| ![Product](docs/screenshots/product-detail.png) | ![Checkout](docs/screenshots/checkout.png) |

| Login | Mobile |
|---|---|
| ![Login](docs/screenshots/login.png) | <img src="docs/screenshots/mobile-product.png" width="260"> |

**Admin panel**

| Dashboard | Products |
|---|---|
| ![Dashboard](docs/screenshots/dashboard.png) | ![Products](docs/screenshots/dashboard-products.png) |

![Reports](docs/screenshots/dashboard-reports.png)

### Project structure

```
apps/
  accounts/    users, addresses, login and sign up
  catalog/     products, categories, banners, comments, wishlist
  cart/        shopping cart
  orders/      checkout, orders, discount codes, shipping
  payments/    payment gateway layer
  dashboard/   custom admin panel
  common/      shared validators and template filters
k2_store/      settings and main urls
templates/
static/
```

---

<div dir="rtl">

## فارسی

k2mod  فروشگاه اینترنتی برای فروش کادو، لوازم آرایشی، پوشاک و اکسسوریه که با جنگو نوشته شده. سایت فارسی و راست‌چینه، قیمت‌ها به تومان و تاریخ‌ها شمسی.

**دموی آنلاین (فقط صفحه اصلی):** https://alisamadzadeh46.github.io/K2mod/

### امکانات

**فروشگاه**
- ثبت‌نام و ورود با شماره موبایل، بازیابی رمز عبور از طریق ایمیل
- دسته‌بندی و زیردسته، برند، رنگ و سایز
- لیست محصولات با فیلتر (بازه‌ی قیمت، رنگ، سایز، کالاهای موجود) و مرتب‌سازی
- صفحه‌ی محصول با گالری تصاویر و انتخاب رنگ و سایز
- جستجو
- لیست علاقه‌مندی‌ها
- ثبت نظر برای محصولات (بعد از تأیید مدیر نمایش داده می‌شه)
- سبد خرید برای کاربر مهمان
- تسویه حساب با کد تخفیف و هزینه‌ی ارسال (ارسال رایگان بالای یه مبلغ مشخص)
- تاریخچه‌ی سفارش‌ها، کد رهگیری مرسوله و مدیریت آدرس‌ها توی حساب کاربری
- ریسپانسیو

**پنل مدیریت اختصاصی**
- داشبورد با آمار فروش، سفارش‌ها، کاربرهای جدید و آخرین فعالیت‌ها
- مدیریت محصولات (ویرایشگر متن، چند تصویر، فیلدهای سئو)
- مدیریت دسته‌بندی‌ها، برندها و رنگ‌ها
- سفارش‌ها: تغییر وضعیت، ثبت شرکت حمل و کد رهگیری
- کدهای تخفیف (درصدی یا مبلغ ثابت، با تقویم شمسی)
- تنظیمات هزینه‌ی ارسال
- تأیید نظرها و پاسخ دادن بهشون
- مدیریت کاربرها (فعال و غیرفعال کردن، دادن دسترسی مدیریت)
- گزارش فروش

**امنیت**
- محدود کردن تلاش‌های ناموفق ورود با django-axes
- هش رمز عبور با Argon2
- آدرس پنل مدیریت از `.env` تنظیم می‌شه

### تکنولوژی‌های استفاده‌شده

- **بک‌اند:** Python و Django 6
- **دیتابیس:** PostgreSQL
- **فرانت‌اند:** HTML، CSS، JavaScript (بدون فریم‌ورک) و قالب‌های جنگو
- **آیکون و فونت:** Remix Icon و وزیرمتن
- **پکیج‌های دیگه:** django-environ، django-axes، argon2-cffi، Pillow، jdatetime، arabic-reshaper، python-bidi
- **دیپلوی:** Gunicorn

### نحوه‌ی اجرا

پیش‌نیازها: Python 3.12 به بالا و PostgreSQL

</div>

```bash
git clone https://github.com/alisamadzadeh46/k2mod.git
cd k2mod

python -m venv venv
venv\Scripts\activate           # on Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
```

<div dir="rtl">

یه دیتابیس PostgreSQL بسازید و فایل `.env` رو از روی `.env.example` درست کنید:

</div>

```bash
copy .env.example .env          # on Linux/macOS: cp .env.example .env
```

<div dir="rtl">

مقدارهای `SECRET_KEY`، `DB_NAME`، `DB_USER`، `DB_PASSWORD` و `DJANGO_ADMIN_URL_PREFIX` رو پر کنید.

</div>

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

<div dir="rtl">

بعد آدرس http://127.0.0.1:8000 رو باز کنید. پنل مدیریت روی `/panel-control/` هست (با `DASHBOARD_URL_PREFIX` قابل تغییره).

برای اضافه کردن چند محصول نمونه:

</div>

```bash
python manage.py seed_demo_data
```

<div dir="rtl">

### تصاویر

تصاویر در [بخش Screenshots](#screenshots).

</div>
