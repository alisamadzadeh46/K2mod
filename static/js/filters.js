const FA_DIGITS = ["۰", "۱", "۲", "۳", "۴", "۵", "۶", "۷", "۸", "۹"];

function faNumber(value) {
    return String(value).replace(/[0-9]/g, (d) => FA_DIGITS[d]);
}

function faGrouped(value) {
    return faNumber(Number(value).toLocaleString("en-US").replace(/,/g, "٬"));
}

function initPriceRange() {
    const root = document.querySelector(".price-range");
    if (!root) return;

    const lo = Number(root.dataset.min);
    const hi = Number(root.dataset.max);
    const rangeMin = root.querySelector("#rangeMin");
    const rangeMax = root.querySelector("#rangeMax");
    const fill = root.querySelector("#rangeFill");
    const minLabel = root.querySelector("#priceMinLabel");
    const maxLabel = root.querySelector("#priceMaxLabel");
    const minInput = root.querySelector("#minPriceInput");
    const maxInput = root.querySelector("#maxPriceInput");

    if (hi <= lo) {
        root.style.display = "none";
        return;
    }

    let curMin = minInput.value ? Number(minInput.value) : lo;
    let curMax = maxInput.value ? Number(maxInput.value) : hi;
    curMin = Math.max(lo, Math.min(curMin, hi));
    curMax = Math.max(lo, Math.min(curMax, hi));
    rangeMin.value = curMin;
    rangeMax.value = curMax;

    function render() {
        const a = Number(rangeMin.value);
        const b = Number(rangeMax.value);
        const left = ((a - lo) / (hi - lo)) * 100;
        const right = ((b - lo) / (hi - lo)) * 100;
        fill.style.right = left + "%";
        fill.style.left = 100 - right + "%";
        minLabel.textContent = faGrouped(a);
        maxLabel.textContent = faGrouped(b);
        minInput.value = a;
        maxInput.value = b;
    }

    rangeMin.addEventListener("input", () => {
        if (Number(rangeMin.value) > Number(rangeMax.value)) rangeMin.value = rangeMax.value;
        render();
    });
    rangeMax.addEventListener("input", () => {
        if (Number(rangeMax.value) < Number(rangeMin.value)) rangeMax.value = rangeMin.value;
        render();
    });

    render();
}

function initCustomSelects() {
    const selects = document.querySelectorAll(".custom-select");

    selects.forEach((select) => {
        const trigger = select.querySelector(".cs-trigger");
        const current = select.querySelector(".cs-current");
        const hidden = select.querySelector("input[type=hidden]");
        const autosubmit = select.dataset.autosubmit === "1";

        trigger.addEventListener("click", (e) => {
            e.stopPropagation();
            // Close any other open dropdown first.
            selects.forEach((s) => s !== select && s.classList.remove("open"));
            select.classList.toggle("open");
        });

        select.querySelectorAll(".cs-option").forEach((option) => {
            option.addEventListener("click", () => {
                hidden.value = option.dataset.value;
                current.textContent = option.textContent.trim();
                select.querySelectorAll(".cs-option").forEach((o) => o.classList.remove("selected"));
                option.classList.add("selected");
                select.classList.remove("open");
                if (autosubmit) select.closest("form").submit();
            });
        });
    });

    document.addEventListener("click", () => {
        selects.forEach((s) => s.classList.remove("open"));
    });
}

document.addEventListener("DOMContentLoaded", function () {
    initPriceRange();
    initCustomSelects();

    document.querySelectorAll("input[type=checkbox][data-autosubmit='1']").forEach((cb) => {
        cb.addEventListener("change", () => cb.closest("form").submit());
    });
});
