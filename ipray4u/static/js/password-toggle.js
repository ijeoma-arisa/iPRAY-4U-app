document.querySelectorAll("[data-password-toggle]").forEach((button) => {
  button.addEventListener("click", () => {
    const input = document.getElementById(button.dataset.passwordToggle);
    if (!input) return;

    const passwordIsVisible = input.type === "text";

    input.type = passwordIsVisible ? "password" : "text";
    button.textContent = passwordIsVisible ? "Show" : "Hide";
    button.setAttribute(
      "aria-label",
      button.getAttribute("aria-label").replace(
        passwordIsVisible ? "Hide" : "Show",
        passwordIsVisible ? "Show" : "Hide",
      ),
    );
    button.setAttribute("aria-pressed", String(!passwordIsVisible));
  });
});
