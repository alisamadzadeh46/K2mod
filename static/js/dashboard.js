function initSidebar() {
    const toggle = document.getElementById("dbMenuToggle");
    const sidebar = document.getElementById("dashboardSidebar");
    const overlay = document.getElementById("sidebarOverlay");
    if (!toggle || !sidebar) return;

    function open() {
        sidebar.classList.add("open");
        if (overlay) overlay.classList.add("show");
        document.body.classList.add("nav-open");
    }
    function close() {
        sidebar.classList.remove("open");
        if (overlay) overlay.classList.remove("show");
        document.body.classList.remove("nav-open");
    }
    toggle.addEventListener("click", open);
    if (overlay) overlay.addEventListener("click", close);
    // Close after tapping any sidebar link (mobile).
    sidebar.querySelectorAll("a").forEach((a) => a.addEventListener("click", close));
    document.addEventListener("keydown", (e) => e.key === "Escape" && close());
}

function initUploadZone() {
    const uploadZone = document.querySelector(".file-upload");
    if (!uploadZone) return;
    const fileInput = uploadZone.querySelector('input[type="file"]');
    const pickBtn = uploadZone.querySelector("#imagePickBtn");
    const filenameEl = uploadZone.querySelector("#uploadFilename");

    function showName() {
        if (filenameEl) {
            filenameEl.textContent = fileInput.files.length ? fileInput.files[0].name : "فایلی انتخاب نشده";
            filenameEl.classList.toggle("has-file", fileInput.files.length > 0);
        }
    }

    if (pickBtn) pickBtn.addEventListener("click", () => fileInput.click());
    fileInput.addEventListener("change", showName);

    uploadZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        uploadZone.classList.add("dragover");
    });
    uploadZone.addEventListener("dragleave", () => uploadZone.classList.remove("dragover"));
    uploadZone.addEventListener("drop", (e) => {
        e.preventDefault();
        uploadZone.classList.remove("dragover");
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            showName();
        }
    });
}

function enhanceSelects() {
    const selects = document.querySelectorAll("select.db-enhance");

    selects.forEach((select) => {
        select.classList.remove("db-enhance");
        select.style.display = "none";

        const wrap = document.createElement("div");
        wrap.className = "db-select";

        const trigger = document.createElement("button");
        trigger.type = "button";
        trigger.className = "db-select-trigger";
        const label = document.createElement("span");
        label.textContent = select.options[select.selectedIndex] ? select.options[select.selectedIndex].text : "";
        trigger.appendChild(label);
        const caret = document.createElement("i");
        caret.className = "ri-arrow-down-s-line";
        trigger.appendChild(caret);

        const list = document.createElement("div");
        list.className = "db-select-options";

        Array.from(select.options).forEach((opt, index) => {
            const item = document.createElement("div");
            item.className = "db-select-option" + (index === select.selectedIndex ? " selected" : "");
            item.textContent = opt.text;
            item.addEventListener("click", () => {
                select.selectedIndex = index;
                select.dispatchEvent(new Event("change", { bubbles: true }));
                label.textContent = opt.text;
                list.querySelectorAll(".db-select-option").forEach((o) => o.classList.remove("selected"));
                item.classList.add("selected");
                wrap.classList.remove("open");
            });
            list.appendChild(item);
        });

        trigger.addEventListener("click", (e) => {
            e.stopPropagation();
            document.querySelectorAll(".db-select.open").forEach((s) => s !== wrap && s.classList.remove("open"));
            wrap.classList.toggle("open");
        });

        wrap.appendChild(trigger);
        wrap.appendChild(list);
        select.parentNode.insertBefore(wrap, select.nextSibling);
    });

    document.addEventListener("click", () => {
        document.querySelectorAll(".db-select.open").forEach((s) => s.classList.remove("open"));
    });
}

window.enhanceSelects = enhanceSelects;

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

document.addEventListener("DOMContentLoaded", function () {
    initSidebar();
    initUploadZone();
    enhanceSelects();
    initFlashMessages();
});
