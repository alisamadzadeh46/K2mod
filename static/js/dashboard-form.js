const FA = ["۰", "۱", "۲", "۳", "۴", "۵", "۶", "۷", "۸", "۹"];
const faNum = (v) => String(v).replace(/[0-9]/g, (d) => FA[d]);

function csrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.content : "";
}

/* Live money grouping */
function initMoneyInputs() {
    document.querySelectorAll("input.db-money").forEach((input) => {
        function format() {
            const latin = input.value
                .replace(/[۰-۹]/g, (d) => FA.indexOf(d))
                .replace(/[٠-٩]/g, (d) => "٠١٢٣٤٥٦٧٨٩".indexOf(d));
            const digits = latin.replace(/\D/g, "");
            input.value = digits ? faNum(Number(digits).toLocaleString("en-US")) : "";
        }
        input.addEventListener("input", format);
        format();
    });

    const form = document.querySelector("form");
    if (form) {
        form.addEventListener("submit", () => {
            document.querySelectorAll("input.db-money").forEach((input) => {
                let v = input.value;
                FA.forEach((d, i) => (v = v.split(d).join(i)));
                input.value = v.replace(/\D/g, "");
            });
        });
    }
}

/* Rich-text editor */
function initRichEditor() {
    const textarea = document.querySelector("textarea.db-richtext");
    if (!textarea) return;

    textarea.style.display = "none";

    const wrap = document.createElement("div");
    wrap.className = "db-editor";

    const tools = [
        ["bold", "ri-bold", "درشت"],
        ["italic", "ri-italic", "کج"],
        ["underline", "ri-underline", "زیرخط"],
        ["formatBlock:h2", "ri-h-2", "تیتر"],
        ["formatBlock:h3", "ri-h-3", "زیرتیتر"],
        ["insertUnorderedList", "ri-list-unordered", "فهرست"],
        ["insertOrderedList", "ri-list-ordered", "فهرست عددی"],
        ["createLink", "ri-link", "پیوند"],
        ["justifyRight", "ri-align-right", "راست‌چین"],
        ["justifyCenter", "ri-align-center", "وسط‌چین"],
        ["removeFormat", "ri-format-clear", "پاک‌سازی"],
    ];

    const toolbar = document.createElement("div");
    toolbar.className = "db-editor-toolbar";
    tools.forEach(([cmd, icon, title]) => {
        const b = document.createElement("button");
        b.type = "button";
        b.title = title;
        b.innerHTML = `<i class="${icon}"></i>`;
        b.addEventListener("click", (e) => {
            e.preventDefault();
            area.focus();
            if (cmd.startsWith("formatBlock:")) {
                document.execCommand("formatBlock", false, cmd.split(":")[1]);
            } else if (cmd === "createLink") {
                const url = prompt("نشانی پیوند را وارد کنید:", "https://");
                if (url) document.execCommand("createLink", false, url);
            } else {
                document.execCommand(cmd, false, null);
            }
            sync();
        });
        toolbar.appendChild(b);
    });

    const area = document.createElement("div");
    area.className = "db-editor-area";
    area.contentEditable = "true";
    area.innerHTML = textarea.value || "";

    function sync() {
        textarea.value = area.innerHTML;
    }
    area.addEventListener("input", sync);

    wrap.appendChild(toolbar);
    wrap.appendChild(area);
    textarea.parentNode.insertBefore(wrap, textarea.nextSibling);

    const form = textarea.closest("form");
    if (form) form.addEventListener("submit", sync);
}

/* SEO analyzer */
function initSeoAnalyzer() {
    const section = document.getElementById("seoSection");
    if (!section) return;

    const nameInput = document.getElementById("id_name");
    const titleInput = document.querySelector(".seo-title");
    const descInput = document.querySelector(".seo-desc");
    const slugInput = document.getElementById("id_slug");
    const descRich = document.querySelector("textarea.db-richtext");

    const previewTitle = document.getElementById("seoPreviewTitle");
    const previewDesc = document.getElementById("seoPreviewDesc");
    const previewSlug = document.getElementById("seoPreviewSlug");
    const titleCounter = document.getElementById("titleCounter");
    const descCounter = document.getElementById("descCounter");
    const checksEl = document.getElementById("seoChecks");

    function analyze() {
        const name = nameInput ? nameInput.value.trim() : "";
        const title = (titleInput.value.trim() || (name ? name + " | فروشگاه k2mod" : ""));
        const desc = descInput.value.trim();
        const slug = (slugInput && slugInput.value.trim()) || (name ? name.replace(/\s+/g, "-") : "product");

        previewTitle.textContent = title || "عنوان محصول";
        previewDesc.textContent = desc || "توضیحات متا اینجا نمایش داده می‌شود…";
        previewSlug.textContent = slug;

        const tl = title.length;
        const dl = desc.length;
        titleCounter.textContent = faNum(tl) + " کاراکتر";
        descCounter.textContent = faNum(dl) + " کاراکتر";
        titleCounter.className = "seo-counter " + (tl >= 30 && tl <= 60 ? "ok" : tl ? "warn" : "bad");
        descCounter.className = "seo-counter " + (dl >= 70 && dl <= 160 ? "ok" : dl ? "warn" : "bad");

        const bodyText = descRich ? (descRich.value || "").replace(/<[^>]*>/g, " ") : "";
        const checks = [
            [tl > 0, "عنوان سئو وارد شده است", "عنوان سئو خالی است"],
            [tl >= 30 && tl <= 60, "طول عنوان مناسب است (۳۰ تا ۶۰ کاراکتر)", "طول عنوان مناسب نیست"],
            [dl > 0, "توضیحات متا وارد شده است", "توضیحات متا خالی است"],
            [dl >= 70 && dl <= 160, "طول توضیحات مناسب است (۷۰ تا ۱۶۰ کاراکتر)", "طول توضیحات مناسب نیست"],
            [name && title.includes(name.split(" ")[0]), "نام محصول در عنوان آمده است", "بهتر است نام محصول در عنوان بیاید"],
            [bodyText.trim().length >= 120, "توضیحات محصول به اندازه کافی کامل است", "توضیحات محصول کوتاه است"],
        ];

        checksEl.innerHTML = checks
            .map(([ok, good, bad]) => {
                const cls = ok ? "ok" : "warn";
                const icon = ok ? "ri-checkbox-circle-fill" : "ri-error-warning-fill";
                return `<li class="${cls}"><i class="${icon}"></i> ${ok ? good : bad}</li>`;
            })
            .join("");
    }

    [nameInput, titleInput, descInput, slugInput].forEach((el) => el && el.addEventListener("input", analyze));
    if (descRich) {
        const richArea = document.querySelector(".db-editor-area");
        if (richArea) richArea.addEventListener("input", analyze);
    }
    analyze();
}

/* Quick-add Brand / Color */
function initQuickAdd() {
    document.querySelectorAll(".db-quick-add").forEach((btn) => {
        btn.addEventListener("click", () => {
            const kind = btn.dataset.quickAdd;
            const prompts = {
                brand: "نام برند جدید:",
                color: "نام رنگ جدید:",
                "color-chip": "نام رنگ جدید:",
                category: "نام دسته‌بندی جدید:",
            };
            const name = prompt(prompts[kind] || "نام جدید:");
            if (!name) return;

            const body = new URLSearchParams({ name });
            if (kind === "color" || kind === "color-chip") {
                const hex = prompt("کد رنگ (مثلاً #ca1250) — اختیاری:", "#cccccc") || "#cccccc";
                body.append("hex_code", hex);
            }

            fetch(btn.dataset.url, {
                method: "POST",
                headers: { "X-CSRFToken": csrfToken(), "Content-Type": "application/x-www-form-urlencoded" },
                body,
            })
                .then((r) => r.json())
                .then((data) => {
                    if (data.error) {
                        alert(data.error);
                        return;
                    }
                    if (kind === "color-chip") {
                        const chips = document.getElementById("colorChips");
                        const container = chips.querySelector("div, ul") || chips;
                        const wrap = document.createElement("div");
                        wrap.innerHTML =
                            `<label><input type="checkbox" name="colors" value="${data.id}" checked> ${data.name}</label>`;
                        container.appendChild(wrap);
                        return;
                    }
                    const select = btn.closest(".db-field-with-add").querySelector("select");
                    const opt = new Option(data.name, data.id, true, true);
                    select.add(opt);
                    select.dispatchEvent(new Event("change", { bubbles: true }));
                    rebuildEnhancedSelect(select);
                });
        });
    });
}

function rebuildEnhancedSelect(select) {
    const old = select.parentNode.querySelector(".db-select");
    if (old) old.remove();
    select.classList.add("db-enhance");
    if (window.enhanceSelects) window.enhanceSelects();
}

/* Coupon form: show only the field that matches the chosen discount type */
function initCouponTypeToggle() {
    const typeSelect = document.getElementById("id_discount_type");
    const percentGroup = document.getElementById("percentGroup");
    const amountGroup = document.getElementById("amountGroup");
    if (!typeSelect || !percentGroup || !amountGroup) return;

    function apply() {
        const isPercent = typeSelect.value === "percent";
        percentGroup.style.display = isPercent ? "" : "none";
        amountGroup.style.display = isPercent ? "none" : "";
    }
    typeSelect.addEventListener("change", apply);
    apply();
}

document.addEventListener("DOMContentLoaded", function () {
    initMoneyInputs();
    initRichEditor();
    initSeoAnalyzer();
    initQuickAdd();
    initCouponTypeToggle();
});
