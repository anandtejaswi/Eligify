/**
 * Security utilities for XSS protection
 */

/**
 * Escape HTML to prevent XSS attacks.
 * @param {string} text - Text to escape
 * @returns {string} Escaped HTML string
 */
export function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return String(text).replace(/[&<>"']/g, m => map[m]);
}

/**
 * Safely set text content (prevents XSS).
 * @param {HTMLElement} element - Element to set text on
 * @param {string} text - Text to set
 */
export function setTextContent(element, text) {
    if (element) {
        element.textContent = text;
    }
}

