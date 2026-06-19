const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

export function fetchWithCsrf(url, options = {}) {
  return fetch(url, {
    ...options,
    headers: {
      "X-CSRFToken": csrfToken,
      ...options.headers,
    },
  });
}