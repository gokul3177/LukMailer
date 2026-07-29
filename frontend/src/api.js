/**
 * api.js — Centralised API base URL helper.
 */

const BASE = import.meta.env.VITE_API_URL
  ? import.meta.env.VITE_API_URL.replace(/\/$/, '')  // strip trailing slash
  : '';                                                // same-origin fallback

/**
 * Build a full API URL.
 * @param {string} path - e.g. "/api/health"
 * @returns {string}
 */
export function apiUrl(path) {
  return `${BASE}${path}`;
}

/**
 * Build a full EventSource URL (SSE).
 * @param {string} path - e.g. "/api/stream-logs"
 * @returns {string}
 */
export function sseUrl(path) {
  return `${BASE}${path}`;
}

/**
 * Check if the backend API URL is configured or running on localhost.
 * @returns {boolean}
 */
export function isApiConfigured() {
  if (import.meta.env.VITE_API_URL) return true;
  if (typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')) {
    return true;
  }
  return false;
}
