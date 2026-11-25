document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.querySelector(".app-nav-toggle");
    const navigation = document.querySelector("#app-navigation");

    if (!toggle || !navigation) {
        return;
    }

    function closeMenu() {
        navigation.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
    }

    toggle.addEventListener("click", () => {
        const isOpen = navigation.classList.toggle("is-open");

        toggle.setAttribute(
            "aria-expanded",
            String(isOpen)
        );
    });

    navigation.addEventListener("click", (event) => {
        if (event.target.closest("a")) {
            closeMenu();
        }
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            closeMenu();
        }
    });

    document.addEventListener("click", (event) => {
        if (
            !navigation.contains(event.target) &&
            !toggle.contains(event.target)
        ) {
            closeMenu();
        }
    });
});