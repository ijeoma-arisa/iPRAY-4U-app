const eyeOpenIcon = `
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z"></path>
    <circle cx="12" cy="12" r="3"></circle>
  </svg>
`;

const eyeSlashedIcon = `
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <path d="m3 3 18 18"></path>
    <path d="M6.7 6.7C4 8.1 2 12 2 12s3.5 7 10 7c1.5 0 2.9-.4 4.1-1"></path>
    <path d="M9.9 5.2A11 11 0 0 1 12 5c6.5 0 10 7 10 7a18 18 0 0 1-2.3 3.3"></path>
    <path d="M10.6 10.6a2 2 0 0 0 2.8 2.8"></path>
  </svg>
`;

const passwordToggleButtons = [
  ...document.querySelectorAll("[data-password-toggle]"),
];

function updateToggleButton(button, passwordsAreVisible) {
  const currentLabel = button.getAttribute("aria-label") || "Show passwords";
  const labelSubject = currentLabel.replace(/^(Show|Hide)\s+/, "");

  button.innerHTML = passwordsAreVisible ? eyeSlashedIcon : eyeOpenIcon;
  button.setAttribute(
    "aria-label",
    `${passwordsAreVisible ? "Hide" : "Show"} ${labelSubject}`,
  );
  button.setAttribute("aria-pressed", String(passwordsAreVisible));
}

passwordToggleButtons.forEach((button) => {
  const targetIds = button.dataset.passwordToggle.split(/\s+/).filter(Boolean);
  const inputs = targetIds
    .map((id) => document.getElementById(id))
    .filter(Boolean);

  if (!inputs.length) return;

  updateToggleButton(button, inputs.every((input) => input.type === "text"));

  button.addEventListener("click", () => {
    const passwordsAreVisible = inputs.every((input) => input.type === "text");
    const showPasswords = !passwordsAreVisible;

    inputs.forEach((input) => {
      input.type = showPasswords ? "text" : "password";
    });

    passwordToggleButtons
      .filter(
        (groupButton) =>
          groupButton.dataset.passwordToggle === button.dataset.passwordToggle,
      )
      .forEach((groupButton) => {
        updateToggleButton(groupButton, showPasswords);
      });
  });
});
