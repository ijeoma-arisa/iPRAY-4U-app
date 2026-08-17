const SUCCESS_DURATION_MS = 2500;
const QUEUED_SUCCESS_KEY = 'ipray4u-mutation-success';

let dismissTimeout;

class MutationApplicationError extends Error {}

export function setMutationPending(
  button,
  pendingName,
  { region, compact = false } = {},
) {
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
  button.innerHTML = `
    <span
      class="mutation-spinner${compact ? ' mutation-spinner-small' : ''}"
      aria-hidden="true"
    ></span>`;
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

  if (state.ariaLabel === null) {
    button.removeAttribute('aria-label');
  } else {
    button.setAttribute('aria-label', state.ariaLabel);
  }

  state.region?.removeAttribute('aria-busy');
}

export async function mutationResponse(response, fallbackMessage) {
  if (!response) throw new Error('Mutation response was unavailable.');

  const responseText = await response.text();
  if (!responseText.trim()) {
    if (response.ok) return null;
    throw new MutationApplicationError(fallbackMessage);
  }

  const result = JSON.parse(responseText);
  if (!response.ok || result.status !== 'success') {
    throw new MutationApplicationError(result.message || fallbackMessage);
  }

  return result;
}

export function mutationErrorMessage(error, fallbackMessage) {
  if (error instanceof MutationApplicationError) return error.message;

  console.error(fallbackMessage, error);
  return fallbackMessage;
}

export function clearMutationFeedback() {
  window.clearTimeout(dismissTimeout);
  document.querySelector('.mutation-feedback-region-js')?.replaceChildren();
}

export function showMutationFeedback(
  message,
  type,
  { autoDismiss = false } = {},
) {
  const container = document.querySelector('.mutation-feedback-region-js');
  if (!container) return null;

  clearMutationFeedback();

  const feedback = document.createElement('div');
  feedback.className = `mutation-feedback mutation-feedback-${type}`;
  feedback.setAttribute('role', type === 'error' ? 'alert' : 'status');

  const messageElement = document.createElement('p');
  messageElement.textContent = message;
  feedback.append(messageElement);

  if (type === 'error') {
    const closeButton = document.createElement('button');
    closeButton.type = 'button';
    closeButton.className = 'mutation-feedback-close';
    closeButton.setAttribute('aria-label', 'Dismiss error message');
    closeButton.textContent = '\u00d7';
    closeButton.addEventListener('click', clearMutationFeedback);
    feedback.append(closeButton);
  }

  container.append(feedback);

  if (autoDismiss) {
    dismissTimeout = window.setTimeout(
      clearMutationFeedback,
      SUCCESS_DURATION_MS,
    );
  }

  return feedback;
}

export function queueMutationSuccess(message) {
  window.sessionStorage.setItem(QUEUED_SUCCESS_KEY, message);
}

export function showQueuedMutationSuccess() {
  const message = window.sessionStorage.getItem(QUEUED_SUCCESS_KEY);
  if (!message) return;

  window.sessionStorage.removeItem(QUEUED_SUCCESS_KEY);
  showMutationFeedback(message, 'success', { autoDismiss: true });
}
