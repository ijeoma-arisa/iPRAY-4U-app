import { afterEach, beforeEach, describe, expect, it } from 'vitest';

import {
  initResetPasswordForm,
} from '../../ipray4u/static/js/reset-password.js';

function submitEvent() {
  return new SubmitEvent('submit', {
    bubbles: true,
    cancelable: true,
  });
}

describe('reset password submission protection', () => {
  let form;
  let password;
  let confirmPassword;
  let submitButton;
  let cleanup;

  beforeEach(() => {
    document.body.innerHTML = `
      <form class="reset-password-form-js">
        <input id="password" required minlength="8">
        <input id="confirm-password" required minlength="8">
        <button type="submit">Reset Password</button>
      </form>
    `;

    form = document.querySelector('form');
    password = document.querySelector('#password');
    confirmPassword = document.querySelector('#confirm-password');
    submitButton = document.querySelector('button[type="submit"]');
    password.value = 'valid-password';
    confirmPassword.value = 'valid-password';

    cleanup = initResetPasswordForm();
  });

  afterEach(() => {
    cleanup();
  });

  it('allows the first valid submission to proceed normally', () => {
    const event = submitEvent();

    const submitted = form.dispatchEvent(event);

    expect(submitted).toBe(true);
    expect(event.defaultPrevented).toBe(false);
    expect(form.dataset.submitting).toBe('true');
  });

  it('disables the button and displays its pending state', () => {
    form.dispatchEvent(submitEvent());

    expect(submitButton.disabled).toBe(true);
    expect(submitButton.textContent).toBe('Resetting…');
    expect(submitButton.getAttribute('aria-busy')).toBe('true');
  });

  it('prevents a second submission while the first is pending', () => {
    form.dispatchEvent(submitEvent());
    const duplicateEvent = submitEvent();

    const submitted = form.dispatchEvent(duplicateEvent);

    expect(submitted).toBe(false);
    expect(duplicateEvent.defaultPrevented).toBe(true);
  });

  it('prevents a repeated keyboard-triggered submission', () => {
    const firstKeyboardEvent = submitEvent();
    const repeatedKeyboardEvent = submitEvent();

    expect(firstKeyboardEvent.submitter).toBeNull();
    expect(form.dispatchEvent(firstKeyboardEvent)).toBe(true);
    expect(repeatedKeyboardEvent.submitter).toBeNull();
    expect(form.dispatchEvent(repeatedKeyboardEvent)).toBe(false);
    expect(repeatedKeyboardEvent.defaultPrevented).toBe(true);
  });

  it('does not enter the pending state when native validation fails', () => {
    password.value = '';
    const event = submitEvent();

    const submitted = form.dispatchEvent(event);

    expect(form.checkValidity()).toBe(false);
    expect(submitted).toBe(true);
    expect(event.defaultPrevented).toBe(false);
    expect(form.dataset.submitting).toBeUndefined();
    expect(submitButton.disabled).toBe(false);
    expect(submitButton.textContent).toBe('Reset Password');
    expect(submitButton.hasAttribute('aria-busy')).toBe(false);
  });

  it('restores the form and button on pageshow', () => {
    form.dispatchEvent(submitEvent());

    window.dispatchEvent(new Event('pageshow'));

    expect(form.dataset.submitting).toBeUndefined();
    expect(submitButton.disabled).toBe(false);
    expect(submitButton.textContent).toBe('Reset Password');
    expect(submitButton.hasAttribute('aria-busy')).toBe(false);
  });

  it('allows a new valid submission after pageshow restores the form', () => {
    form.dispatchEvent(submitEvent());
    window.dispatchEvent(new Event('pageshow'));
    const nextEvent = submitEvent();

    const submitted = form.dispatchEvent(nextEvent);

    expect(submitted).toBe(true);
    expect(nextEvent.defaultPrevented).toBe(false);
    expect(form.dataset.submitting).toBe('true');
    expect(submitButton.disabled).toBe(true);
    expect(submitButton.textContent).toBe('Resetting…');
    expect(submitButton.getAttribute('aria-busy')).toBe('true');
  });
});
