const PERSIAN_DIGITS = ["۰", "۱", "۲", "۳", "۴", "۵", "۶", "۷", "۸", "۹"];

function toPersianNumber(value) {
    return String(value).replace(/[0-9]/g, (digit) => PERSIAN_DIGITS[digit]);
}

function formatToman(value) {
    const grouped = Number(value).toLocaleString("en-US").replace(/,/g, "٬");
    return toPersianNumber(grouped);
}

function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.content : "";
}

function postForm(url, data) {
    const body = new URLSearchParams(data);
    return fetch(url, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCsrfToken(),
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body,
    }).then((response) => response.json());
}

function renderCart(cartData) {
    const itemsEl = document.getElementById("cartItems");
    const totalEl = document.getElementById("cartTotal");
    const countEls = document.querySelectorAll(".cart-count");

    countEls.forEach((el) => (el.textContent = toPersianNumber(cartData.total_items)));
    if (totalEl) totalEl.textContent = formatToman(cartData.total_price);

    if (!itemsEl) return;

    if (cartData.items.length === 0) {
        itemsEl.innerHTML = '<div class="cart-empty">سبد خرید شما خالی است.</div>';
        return;
    }

    itemsEl.innerHTML = cartData.items
        .map((item) => {
            const variants = [];
            if (item.color) {
                variants.push(
                    `<span class="cart-item-badge"><span class="cart-swatch" style="background:${item.color_hex}"></span>${item.color}</span>`
                );
            }
            if (item.size) variants.push(`<span class="cart-item-badge">سایز ${item.size}</span>`);
            return `
        <div class="cart-item" data-item-id="${item.id}" data-quantity="${item.quantity}">
            <a href="${item.url}" class="cart-item-thumb"><img src="${item.image_url}" alt="${item.name}"></a>
            <div class="cart-item-info">
                <a href="${item.url}" class="cart-item-name">${item.name}</a>
                ${variants.length ? `<div class="cart-item-variants">${variants.join("")}</div>` : ""}
                <div class="cart-item-controls">
                    <div class="qty-controls">
                        <button type="button" class="qty-decrease">-</button>
                        <span>${toPersianNumber(item.quantity)}</span>
                        <button type="button" class="qty-increase">+</button>
                    </div>
                    <button type="button" class="cart-item-remove"><i class="ri-delete-bin-6-line"></i> حذف</button>
                </div>
            </div>
        </div>`;
        })
        .join("");
}

function addToCart(productId, quantity = 1, sizeId = "", colorId = "") {
    const data = { product_id: productId, quantity };
    if (sizeId) data.size_id = sizeId;
    if (colorId) data.color_id = colorId;
    return postForm("/cart/add/", data).then(renderCart);
}

function updateItem(itemId, quantity) {
    return postForm(`/cart/items/${itemId}/update/`, { quantity }).then(renderCart);
}

function removeItem(itemId) {
    return postForm(`/cart/items/${itemId}/remove/`, {}).then(renderCart);
}

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".add-to-cart").forEach((button) => {
        button.addEventListener("click", function () {
            const productId = this.dataset.productId;
            const originalText = this.textContent;
            addToCart(productId).then(() => {
                this.textContent = "افزوده شد!";
                setTimeout(() => (this.textContent = originalText), 1500);
            });
        });
    });

    const itemsEl = document.getElementById("cartItems");
    if (itemsEl) {
        itemsEl.addEventListener("click", (e) => {
            const itemEl = e.target.closest(".cart-item");
            if (!itemEl) return;
            const itemId = itemEl.dataset.itemId;
            const currentQty = parseInt(itemEl.dataset.quantity || "1", 10);

            if (e.target.classList.contains("qty-increase")) {
                updateItem(itemId, currentQty + 1);
            } else if (e.target.classList.contains("qty-decrease")) {
                updateItem(itemId, currentQty - 1);
            } else if (e.target.classList.contains("cart-item-remove")) {
                removeItem(itemId);
            }
        });
    }

    const cartButton = document.getElementById("cartButton");
    const cartModal = document.getElementById("cartModal");
    const closeModal = document.getElementById("closeModal");
    const backBtn = document.getElementById("backBtn");

    function openCart() {
        if (!cartModal) return;
        cartModal.classList.add("show");
        document.body.style.overflow = "hidden";
    }

    function closeCartModal() {
        if (!cartModal) return;
        cartModal.classList.remove("show");
        document.body.style.overflow = "";
    }

    if (cartButton) cartButton.addEventListener("click", openCart);
    if (closeModal) closeModal.addEventListener("click", closeCartModal);
    if (backBtn) backBtn.addEventListener("click", closeCartModal);

    if (cartModal) {
        cartModal.addEventListener("click", (e) => {
            if (e.target === cartModal) closeCartModal();
        });
    }

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && cartModal && cartModal.classList.contains("show")) {
            closeCartModal();
        }
    });
});
