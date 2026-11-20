const RESETTING_LABEL = "Resetting…";

export function initResetPasswordForm(root = document) {
  const form = root.querySelector(".reset-password-form-js");
  const submitButton = form?.querySelector('button[type="submit"]');

  if (!form || !submitButton) return;

  const originalLabel = submitButton.textContent;

  function handleSubmit(event) {
    if (form.dataset.submitting === "true") {
      event.preventDefault();
      return;
    }

    if (!form.checkValidity()) return;

    form.dataset.submitting = "true";
    submitButton.disabled = true;
    submitButton.textContent = RESETTING_LABEL;
    submitButton.setAttribute("aria-busy", "true");
  }

  function handlePageShow() {
    delete form.dataset.submitting;
    submitButton.disabled = false;
    submitButton.textContent = originalLabel;
    submitButton.removeAttribute("aria-busy");
  }

  form.addEventListener("submit", handleSubmit);
  window.addEventListener("pageshow", handlePageShow);

  return () => {
    form.removeEventListener("submit", handleSubmit);
    window.removeEventListener("pageshow", handlePageShow);
  };
}

initResetPasswordForm();
