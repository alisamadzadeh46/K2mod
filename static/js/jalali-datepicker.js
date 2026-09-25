const FA_DIGITS_DP = ["۰", "۱", "۲", "۳", "۴", "۵", "۶", "۷", "۸", "۹"];
const toFaDigits = (v) => String(v).replace(/[0-9]/g, (d) => FA_DIGITS_DP[d]);
const toLatinDigits = (v) => String(v).replace(/[۰-۹]/g, (d) => FA_DIGITS_DP.indexOf(d));

const JALALI_WEEKDAYS = ["ش", "ی", "د", "س", "چ", "پ", "ج"];
const JALALI_MONTHS = [
    "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند",
];

function jdiv(a, b) {
    return Math.trunc(a / b);
}
function jmod(a, b) {
    return a - Math.trunc(a / b) * b;
}

function g2d(gy, gm, gd) {
    let d = jdiv((gy + jdiv(gm - 8, 6) + 100100) * 1461, 4)
        + jdiv(153 * jmod(gm + 9, 12) + 2, 5) + gd - 34840408;
    d = d - jdiv(jdiv(gy + 100100 + jdiv(gm - 8, 6), 100) * 3, 4) + 752;
    return d;
}

function d2g(jdn) {
    let j = 4 * jdn + 139361631;
    j = j + jdiv(jdiv(4 * jdn + 183187720, 146097) * 3, 4) * 4 - 3908;
    const i = jdiv(jmod(j, 1461), 4) * 5 + 308;
    const gd = jdiv(jmod(i, 153), 5) + 1;
    const gm = jmod(jdiv(i, 153), 12) + 1;
    const gy = jdiv(j, 1461) - 100100 + jdiv(8 - gm, 6);
    return { gy, gm, gd };
}

function jalCal(jy) {
    const breaks = [-61, 9, 38, 199, 426, 686, 756, 818, 1111, 1181, 1210, 1635, 2060, 2097, 2192, 2262, 2324, 2394, 2456, 3178];
    const bl = breaks.length;
    const gy = jy + 621;
    let leapJ = -14;
    let jp = breaks[0];
    let jump = 0;
    let i;
    for (i = 1; i < bl; i += 1) {
        const jm = breaks[i];
        jump = jm - jp;
        if (jy < jm) break;
        leapJ += jdiv(jump, 33) * 8 + jdiv(jmod(jump, 33), 4);
        jp = jm;
    }
    let n = jy - jp;
    leapJ += jdiv(n, 33) * 8 + jdiv(jmod(n, 33) + 3, 4);
    if (jmod(jump, 33) === 4 && jump - n === 4) leapJ += 1;
    const leapG = jdiv(gy, 4) - jdiv((jdiv(gy, 100) + 1) * 3, 4) - 150;
    const march = 20 + leapJ - leapG;
    if (jump - n < 6) n = n - jump + jdiv(jump + 4, 33) * 33;
    let leap = jmod(jmod(n + 1, 33) - 1, 4);
    if (leap === -1) leap = 4;
    return { leap, gy, march };
}

function j2d(jy, jm, jd) {
    const r = jalCal(jy);
    return g2d(r.gy, 3, r.march) + (jm - 1) * 31 - jdiv(jm, 7) * (jm - 7) + jd - 1;
}

function d2j(jdn) {
    const gy = d2g(jdn).gy;
    let jy = gy - 621;
    let r = jalCal(jy);
    const jdn1f = g2d(r.gy, 3, r.march);
    let jm, jd, k = jdn - jdn1f;
    if (k >= 0) {
        if (k <= 185) {
            jm = 1 + jdiv(k, 31);
            jd = jmod(k, 31) + 1;
            return [jy, jm, jd];
        }
        k -= 186;
    } else {
        jy -= 1;
        k += 179;
        if (r.leap === 1) k += 1;
    }
    jm = 7 + jdiv(k, 30);
    jd = jmod(k, 30) + 1;
    return [jy, jm, jd];
}

function isLeapJalaaliYear(jy) {
    return jalCal(jy).leap === 0;
}

function gregorianToJalali(gy, gm, gd) {
    return d2j(g2d(gy, gm, gd));
}

function jalaliToGregorian(jy, jm, jd) {
    const g = d2g(j2d(jy, jm, jd));
    return [g.gy, g.gm, g.gd];
}

function jalaliMonthLength(jy, jm) {
    if (jm <= 6) return 31;
    if (jm <= 11) return 30;
    return isLeapJalaaliYear(jy) ? 30 : 29;
}

function parseJalaliInput(value) {
    const raw = toLatinDigits(value || "").trim();
    const m = raw.match(/^(\d{4})[-/](\d{1,2})[-/](\d{1,2})(?:[ T](\d{1,2}):(\d{2}))?$/);
    if (!m) return null;
    return {
        y: parseInt(m[1], 10), m: parseInt(m[2], 10), d: parseInt(m[3], 10),
        h: m[4] ? parseInt(m[4], 10) : 0, min: m[5] ? parseInt(m[5], 10) : 0,
    };
}

function formatJalaliValue(y, m, d, h, min) {
    const pad = (n) => String(n).padStart(2, "0");
    return toFaDigits(`${y}/${pad(m)}/${pad(d)} ${pad(h)}:${pad(min)}`);
}

function todayJalali() {
    const now = new Date();
    const [jy, jm, jd] = gregorianToJalali(now.getFullYear(), now.getMonth() + 1, now.getDate());
    return { y: jy, m: jm, d: jd, h: now.getHours(), min: now.getMinutes() };
}

function buildPicker(input) {
    const wrap = document.createElement("div");
    wrap.className = "jdp-wrap";
    input.parentNode.insertBefore(wrap, input);
    wrap.appendChild(input);

    const iconBtn = document.createElement("button");
    iconBtn.type = "button";
    iconBtn.className = "jdp-icon-btn";
    iconBtn.innerHTML = '<i class="ri-calendar-line"></i>';
    iconBtn.setAttribute("aria-label", "انتخاب تاریخ");
    wrap.appendChild(iconBtn);

    const popup = document.createElement("div");
    popup.className = "jdp-popup";
    wrap.appendChild(popup);

    let view = todayJalali();
    let selected = parseJalaliInput(input.value);
    if (selected) {
        view = { ...selected };
    }

    function render() {
        const monthLen = jalaliMonthLength(view.y, view.m);
        const [gy, gm, gd] = jalaliToGregorian(view.y, view.m, 1);
        const firstWeekday = (new Date(gy, gm - 1, gd).getDay() + 1) % 7; // shift so Saturday = 0

        let daysHtml = "";
        for (let i = 0; i < firstWeekday; i += 1) daysHtml += '<span class="jdp-day jdp-empty"></span>';
        for (let d = 1; d <= monthLen; d += 1) {
            const isSelected = selected && selected.y === view.y && selected.m === view.m && selected.d === d;
            daysHtml += `<button type="button" class="jdp-day${isSelected ? " selected" : ""}" data-day="${d}">${toFaDigits(d)}</button>`;
        }

        popup.innerHTML = `
            <div class="jdp-header">
                <button type="button" class="jdp-nav" data-nav="prev"><i class="ri-arrow-right-s-line"></i></button>
                <span class="jdp-title">${JALALI_MONTHS[view.m - 1]} ${toFaDigits(view.y)}</span>
                <button type="button" class="jdp-nav" data-nav="next"><i class="ri-arrow-left-s-line"></i></button>
            </div>
            <div class="jdp-weekdays">${JALALI_WEEKDAYS.map((w) => `<span>${w}</span>`).join("")}</div>
            <div class="jdp-days">${daysHtml}</div>
            <div class="jdp-time">
                <span>ساعت</span>
                <div class="jdp-time-inputs">
                    <input type="number" class="jdp-hour" min="0" max="23" value="${selected ? selected.h : view.h}">
                    <span>:</span>
                    <input type="number" class="jdp-min" min="0" max="59" value="${selected ? selected.min : view.min}">
                </div>
            </div>
            <div class="jdp-actions">
                <button type="button" class="jdp-today">امروز</button>
                <button type="button" class="jdp-confirm">تأیید</button>
            </div>
        `;
    }

    function open() {
        render();
        popup.classList.add("show");
    }
    function close() {
        popup.classList.remove("show");
    }

    iconBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        if (popup.classList.contains("show")) {
            close();
        } else {
            const parsed = parseJalaliInput(input.value);
            if (parsed) { selected = parsed; view = { ...parsed }; }
            open();
        }
    });

    popup.addEventListener("click", (e) => {
        const nav = e.target.closest(".jdp-nav");
        if (nav) {
            e.stopPropagation();
            const dir = nav.dataset.nav === "prev" ? -1 : 1;
            view.m += dir;
            if (view.m < 1) { view.m = 12; view.y -= 1; }
            if (view.m > 12) { view.m = 1; view.y += 1; }
            render();
            return;
        }
        const dayBtn = e.target.closest(".jdp-day:not(.jdp-empty)");
        if (dayBtn) {
            e.stopPropagation();
            const hourEl = popup.querySelector(".jdp-hour");
            const minEl = popup.querySelector(".jdp-min");
            selected = {
                y: view.y, m: view.m, d: parseInt(dayBtn.dataset.day, 10),
                h: parseInt(hourEl.value || "0", 10), min: parseInt(minEl.value || "0", 10),
            };
            render();
            return;
        }
        if (e.target.closest(".jdp-today")) {
            e.stopPropagation();
            selected = todayJalali();
            view = { ...selected };
            render();
            return;
        }
        if (e.target.closest(".jdp-confirm")) {
            e.stopPropagation();
            if (!selected) selected = todayJalali();
            const hourEl = popup.querySelector(".jdp-hour");
            const minEl = popup.querySelector(".jdp-min");
            selected.h = parseInt(hourEl.value || "0", 10);
            selected.min = parseInt(minEl.value || "0", 10);
            input.value = formatJalaliValue(selected.y, selected.m, selected.d, selected.h, selected.min);
            input.dispatchEvent(new Event("input", { bubbles: true }));
            close();
        }
    });

    document.addEventListener("click", (e) => {
        if (!wrap.contains(e.target)) close();
    });
}

function initJalaliDatePickers() {
    document.querySelectorAll("input.jalali-datetime-input").forEach((input) => {
        if (input.dataset.jdpInit) return;
        input.dataset.jdpInit = "1";
        buildPicker(input);
    });
}

document.addEventListener("DOMContentLoaded", initJalaliDatePickers);
