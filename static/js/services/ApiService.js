/**
 * API Service - Handles all API communication
 */
export class ApiService {
    /**
     * Parse marksheet PDF
     * @param {File} file - PDF file
     * @param {string} method - Parsing method (auto/text/ocr)
     * @param {number} dpi - DPI for OCR
     * @returns {Promise<Object>}
     */
    async parseMarksheet(file, method = 'auto', dpi = 300) {
        const formData = new FormData();
        formData.append('file', file);
        const url = `/api/parse-marksheet?method=${encodeURIComponent(method)}${dpi ? `&dpi=${encodeURIComponent(dpi)}` : ''}`;

        const response = await fetch(url, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to parse marksheet');
        }

        return await response.json();
    }

    /**
     * Parse PDF
     * @param {File} file - PDF file
     * @param {string} method - Parsing method (auto/text/ocr)
     * @param {number} dpi - DPI for OCR
     * @returns {Promise<Object>}
     */
    async parsePdf(file, method = 'auto', dpi = 300) {
        const formData = new FormData();
        formData.append('file', file);
        const url = `/api/parse-pdf?method=${encodeURIComponent(method)}${dpi ? `&dpi=${encodeURIComponent(dpi)}` : ''}`;

        const response = await fetch(url, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to parse PDF');
        }

        return await response.json();
    }
}

