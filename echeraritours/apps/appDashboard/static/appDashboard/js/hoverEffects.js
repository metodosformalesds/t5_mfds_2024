document.addEventListener("DOMContentLoaded", function () {
    const profileContainer = document.querySelector('.profile-container label[for="profileImageInput"]');
    const coverContainer = document.querySelector('.profile-container label[for="coverPhotoInput"]');

    function addHoverEffect(container) {
        container.addEventListener("mouseenter", () => {
            const img = container.querySelector("img");
            const overlay = container.querySelector(".overlay");
            img.style.filter = "brightness(50%)";
            overlay.style.display = "flex";
        });

        container.addEventListener("mouseleave", () => {
            const img = container.querySelector("img");
            const overlay = container.querySelector(".overlay");
            img.style.filter = "brightness(100%)";
            overlay.style.display = "none";
        });
    }

    addHoverEffect(profileContainer);
    addHoverEffect(coverContainer);
});
