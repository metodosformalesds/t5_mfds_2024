document.getElementById("previousButton").addEventListener("click", function(event) {
    const inputs = document.querySelectorAll("input[required], select[required], textarea[required]");
    inputs.forEach(input => input.removeAttribute("required"));
});