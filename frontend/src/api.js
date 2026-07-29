/**
 * api.js — Centralised API base URL helper.
 *
 * During local development the backend runs on the same origin, so we use
 * relative paths (e.g. /api/health).
 *
 * When deployed with a split setup (Vercel frontend + Railway backend) set the
 * Vercel environment variable:
 *   VITE_API_URL = https://your-app.up.railway.app
 *
 * All fetch calls should import `apiUrl` from this file instead of hardcoding paths.
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
