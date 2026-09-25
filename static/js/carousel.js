function initCarousels() {
    document.querySelectorAll("[data-carousel]").forEach((root) => {
        const track = root.querySelector("[data-carousel-track]");
        if (!track) return;

        const prevBtn = root.querySelector("[data-carousel-prev]");
        const nextBtn = root.querySelector("[data-carousel-next]");
        const dotsWrap = root.querySelector("[data-carousel-dots]");
        const slides = Array.from(track.children);

        function currentIndex() {
            let closest = 0;
            let closestDistance = Infinity;
            slides.forEach((slide, index) => {
                const distance = Math.abs(slide.offsetLeft - track.scrollLeft);
                if (distance < closestDistance) {
                    closestDistance = distance;
                    closest = index;
                }
            });
            return closest;
        }

        function scrollToIndex(index) {
            const clamped = Math.max(0, Math.min(index, slides.length - 1));
            track.scrollTo({ left: slides[clamped].offsetLeft, behavior: "smooth" });
        }

        if (prevBtn) prevBtn.addEventListener("click", () => scrollToIndex(currentIndex() - 1));
        if (nextBtn) nextBtn.addEventListener("click", () => scrollToIndex(currentIndex() + 1));

        if (dotsWrap && slides.length > 1) {
            slides.forEach((_, index) => {
                const dot = document.createElement("button");
                dot.type = "button";
                dot.className = "carousel-dot" + (index === 0 ? " active" : "");
                dot.addEventListener("click", () => scrollToIndex(index));
                dotsWrap.appendChild(dot);
            });

            let scrollTimeout;
            track.addEventListener("scroll", () => {
                clearTimeout(scrollTimeout);
                scrollTimeout = setTimeout(() => {
                    const index = currentIndex();
                    Array.from(dotsWrap.children).forEach((dot, i) => dot.classList.toggle("active", i === index));
                }, 100);
            });
        }
    });
}

document.addEventListener("DOMContentLoaded", initCarousels);
