const form = document.querySelector("form");
const submitButton = form?.querySelector('button[type="submit"]');

form?.addEventListener("submit", () => {
  if (!submitButton || !form.checkValidity()) return;

  submitButton.disabled = true;
  submitButton.textContent = "Sending…";
});

window.addEventListener("pageshow", () => {
  if (!submitButton) return;

  submitButton.disabled = false;
  submitButton.textContent = "Send Reset Link";
});
