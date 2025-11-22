/**
 * Marksheet Scanner View - Handles marksheet scanning UI
 */
import { escapeHtml, setTextContent } from '../utils/security.js';

export class MarksheetScannerView {
    constructor() {
        this.fileInput = document.getElementById('marksheetFile');
        this.methodSelect = document.getElementById('marksheetMethod');
        this.dpiInput = document.getElementById('marksheetDpi');
        this.scanButton = document.getElementById('scanBtn');
        this.messageDiv = document.getElementById('scanMessage');
        this.resultsDiv = document.getElementById('scanResults');
    }

    /**
     * Get form data
     * @returns {Object}
     */
    getFormData() {
        return {
            file: this.fileInput?.files[0] || null,
            method: this.methodSelect?.value || 'auto',
            dpi: this.dpiInput?.value ? parseInt(this.dpiInput.value) : 300
        };
    }

    /**
     * Show message
     * @param {string} message
     * @param {string} type - 'success' | 'error' | 'warning'
     */
    showMessage(message, type = 'info') {
        if (!this.messageDiv) return;

        setTextContent(this.messageDiv, message);
        this.messageDiv.className = 'mt-4 p-3 rounded-lg text-center block';

        switch (type) {
            case 'success':
                this.messageDiv.className += ' bg-green-100 text-green-700';
                break;
            case 'error':
                this.messageDiv.className += ' bg-red-100 text-red-700';
                break;
            case 'warning':
                this.messageDiv.className += ' bg-yellow-100 text-yellow-800';
                break;
            default:
                this.messageDiv.className += ' bg-gray-100 text-gray-700';
        }
    }

    /**
     * Hide message
     */
    hideMessage() {
        if (this.messageDiv) {
            this.messageDiv.textContent = '';
            this.messageDiv.className = 'mt-4 p-3 rounded-lg text-center hidden';
        }
    }

    /**
     * Display scan results
     * @param {Object} fields - Extracted fields
     */
    displayResults(fields) {
        if (!this.resultsDiv) return;

        const subjects = (fields.subjects || []).map(s => `
            <tr>
                <td class="p-2 border">${escapeHtml(s.name ?? '')}</td>
                <td class="p-2 border text-right">${escapeHtml(String(s.marks ?? ''))}</td>
                <td class="p-2 border">${escapeHtml(s.grade ?? '')}</td>
            </tr>
        `).join('');

        this.resultsDiv.innerHTML = `
            <div class="bg-gray-100 border border-gray-300 rounded-lg p-4">
                <h3 class="text-xl font-bold mb-3">Extracted Fields</h3>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div><span class="font-semibold">Name:</span> ${escapeHtml(fields.name ?? '')}</div>
                    <div><span class="font-semibold">Father Name:</span> ${escapeHtml(fields.father_name ?? '')}</div>
                    <div><span class="font-semibold">Roll Number:</span> ${escapeHtml(fields.roll_number ?? '')}</div>
                    <div><span class="font-semibold">Registration Number:</span> ${escapeHtml(fields.registration_number ?? '')}</div>
                    <div><span class="font-semibold">DOB:</span> ${escapeHtml(fields.dob ?? '')}</div>
                    <div><span class="font-semibold">Exam/Course:</span> ${escapeHtml(fields.exam ?? '')}</div>
                    <div><span class="font-semibold">Year:</span> ${escapeHtml(fields.year ?? '')}</div>
                    <div><span class="font-semibold">University/Board:</span> ${escapeHtml(fields.university ?? '')}</div>
                    <div><span class="font-semibold">College/Institute:</span> ${escapeHtml(fields.college ?? '')}</div>
                    <div><span class="font-semibold">Percentage:</span> ${escapeHtml(String(fields.percentage ?? ''))}</div>
                    <div><span class="font-semibold">CGPA:</span> ${escapeHtml(String(fields.cgpa ?? ''))}</div>
                </div>
                <h4 class="text-lg font-semibold mt-4">Subjects</h4>
                <table class="w-full border-collapse mt-2">
                    <thead>
                        <tr class="bg-gray-200">
                            <th class="p-2 border text-left">Subject</th>
                            <th class="p-2 border text-right">Marks</th>
                            <th class="p-2 border text-left">Grade</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${subjects || '<tr><td colspan="3" class="p-2 border text-center text-gray-500">No subjects parsed</td></tr>'}
                    </tbody>
                </table>
            </div>
        `;
    }

    /**
     * Clear results
     */
    clearResults() {
        if (this.resultsDiv) {
            this.resultsDiv.innerHTML = '';
        }
        this.hideMessage();
    }

    /**
     * Set loading state
     * @param {boolean} isLoading
     */
    setLoading(isLoading) {
        if (this.scanButton) {
            this.scanButton.disabled = isLoading;
            this.scanButton.textContent = isLoading ? 'Scanning...' : 'Scan Marksheet';
        }
    }
}

