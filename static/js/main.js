document.addEventListener("DOMContentLoaded", function () {
    const navToggle = document.getElementById("navToggle");
    const mainNav = document.getElementById("mainNav");

    if (navToggle && mainNav) {
        navToggle.addEventListener("click", () => {
            mainNav.classList.toggle("nav-open");
            navToggle.classList.toggle("active");
        });
    }

    const navCategories = document.getElementById("navCategories");
    const navCategoriesBtn = document.getElementById("navCategoriesBtn");
    if (navCategories && navCategoriesBtn) {
        navCategoriesBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            navCategories.classList.toggle("open");
        });
        document.addEventListener("click", (e) => {
            if (!navCategories.contains(e.target)) {
                navCategories.classList.remove("open");
            }
        });
    }

    const cards = document.querySelectorAll(".product-card");
    cards.forEach((card, index) => {
        card.style.opacity = "0";
        card.style.transform = "translateY(16px)";
        card.style.transition = "opacity 0.4s ease, transform 0.4s ease";
        setTimeout(() => {
            card.style.opacity = "1";
            card.style.transform = "translateY(0)";
        }, 80 + index * 60);
    });

    initFavorites();
    initFlashMessages();
    initAddressSelect();
});

function initAddressSelect() {
    const radios = document.querySelectorAll('.address-radio-list input[type="radio"]');
    if (!radios.length) return;

    function sync() {
        radios.forEach((r) => r.closest(".address-radio").classList.toggle("selected", r.checked));
    }
    radios.forEach((r) => r.addEventListener("change", sync));
    sync();
}

function initFavorites() {
    function csrf() {
        const meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.content : "";
    }

    document.addEventListener("click", function (e) {
        const btn = e.target.closest(".fav-btn");
        if (!btn) return;
        e.preventDefault();

        fetch(btn.dataset.favUrl, {
            method: "POST",
            headers: { "X-CSRFToken": csrf(), "Content-Type": "application/x-www-form-urlencoded" },
        })
            .then((r) => {
                if (r.status === 401) {
                    window.location.href = "/accounts/login/";
                    return null;
                }
                return r.json();
            })
            .then((data) => {
                if (!data) return;
                btn.classList.toggle("is-fav", data.favorited);
                const icon = btn.querySelector("i");
                if (icon) icon.className = data.favorited ? "ri-heart-fill" : "ri-heart-line";
                const favPage = btn.closest(".favorites-page");
                if (!data.favorited && favPage) {
                    const card = btn.closest(".product-card");
                    if (card) card.remove();
                    const grid = favPage.querySelector(".favorites-grid");
                    if (grid && grid.children.length === 0) {
                        grid.remove();
                        const empty = document.createElement("div");
                        empty.className = "account-empty";
                        empty.innerHTML =
                            '<i class="ri-heart-line"></i>' +
                            "<p>هنوز محصولی به علاقه‌مندی‌ها اضافه نکرده‌اید.</p>" +
                            '<a href="/" class="btn btn-primary">مشاهده محصولات</a>';
                        favPage.appendChild(empty);
                    }
                }
            });
    });
}

function initFlashMessages() {
    document.querySelectorAll(".messages .message").forEach((msg) => {
        setTimeout(() => {
            msg.style.transition = "opacity 0.4s ease, transform 0.4s ease";
            msg.style.opacity = "0";
            msg.style.transform = "translateY(-8px)";
            setTimeout(() => msg.remove(), 400);
        }, 4000);
    });
}
