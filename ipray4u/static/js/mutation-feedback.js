const SUCCESS_DURATION_MS = 2500;
const QUEUED_SUCCESS_KEY = 'ipray4u-mutation-success';

export function setMutationPending(button, pendingName, { region, compact = false } = {}) {
  if (button.dataset.mutationPending === 'true') return null;

  const state = {
    html: button.innerHTML,
    ariaLabel: button.getAttribute('aria-label'),
    width: button.getBoundingClientRect().width,
    region,
  };

  button.dataset.mutationPending = 'true';
  button.disabled = true;
  button.style.minWidth = `${state.width}px`;
  button.setAttribute('aria-label', pendingName);
  button.setAttribute('aria-busy', 'true');
  button.innerHTML = `<span class="mutation-spinner${compact ? ' mutation-spinner-small' : ''}" aria-hidden="true"></span>`;
  region?.setAttribute('aria-busy', 'true');
  return state;
}

export function restoreMutationControl(button, state) {
  if (!state) return;

  button.innerHTML = state.html;
  button.disabled = false;
  button.style.minWidth = '';
  button.removeAttribute('aria-busy');
  delete button.dataset.mutationPending;

  if (state.ariaLabel === null) button.removeAttribute('aria-label');
  else button.setAttribute('aria-label', state.ariaLabel);

  state.region?.removeAttribute('aria-busy');
}

export function clearMutationFeedback(container) {
  container?.querySelectorAll('.mutation-feedback').forEach(feedback => feedback.remove());
}

export function showMutationFeedback(container, message, type, { autoDismiss = false } = {}) {
  if (!container) return null;

  clearMutationFeedback(container);
  const feedback = document.createElement('p');
  feedback.className = `mutation-feedback mutation-feedback-${type}`;
  feedback.textContent = message;
  feedback.setAttribute('role', type === 'error' ? 'alert' : 'status');
  container.append(feedback);

  if (autoDismiss) {
    window.setTimeout(() => feedback.remove(), SUCCESS_DURATION_MS);
  }

  return feedback;
}

export function mutationErrorMessage(error, fallback) {
  console.error(fallback, error);
  return error?.message || fallback;
}

export function queueMutationSuccess(message) {
  window.sessionStorage.setItem(QUEUED_SUCCESS_KEY, message);
}

export function showQueuedMutationSuccess(container) {
  const message = window.sessionStorage.getItem(QUEUED_SUCCESS_KEY);
  if (!message) return;

  window.sessionStorage.removeItem(QUEUED_SUCCESS_KEY);
  showMutationFeedback(container, message, 'success', { autoDismiss: true });
}
