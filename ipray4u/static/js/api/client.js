import { LOGIN_URL } from './endpoints.js';

const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

export async function fetchWithCsrf(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      "X-CSRFToken": csrfToken,
      ...options.headers,
    },
  });

  if (response.status === 401) {
    window.location.href = LOGIN_URL;
    return;
  }

  return response;
}