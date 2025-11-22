/**
 * Candidate Form View - Handles form display and user input
 */
export class CandidateFormView {
    constructor() {
        this.form = document.getElementById('candidate-form');
        this.formMessage = document.getElementById('form-message');
    }

    /**
     * Get form data
     * @returns {Object}
     */
    getFormData() {
        return {
            firstName: document.getElementById('firstName').value.trim(),
            dob: document.getElementById('dob').value,
            email: document.getElementById('email').value.trim().toLowerCase(),
            category: document.getElementById('category').value,
            p10: document.getElementById('p10').value,
            p12: document.getElementById('p12').value,
            ugCgpa: document.getElementById('ugCgpa').value
        };
    }

    /**
     * Validate decimal precision
     * @param {string} value
     * @returns {boolean}
     */
    hasTooManyDecimals(value) {
        if (value === null || value === undefined) return false;
        const s = String(value).trim();
        if (s === '') return false;
        const m = s.match(/^\d+(?:\.(\d+))?$/);
        return m && m[1] && m[1].length > 3;
    }

    /**
     * Validate form input
     * @returns {Object} {isValid: boolean, error: string}
     */
    validateInput() {
        const data = this.getFormData();
        const p10Raw = data.p10;
        const p12Raw = data.p12;
        const ugRaw = data.ugCgpa;

        if (this.hasTooManyDecimals(p10Raw) || 
            this.hasTooManyDecimals(p12Raw) || 
            this.hasTooManyDecimals(ugRaw)) {
            return {
                isValid: false,
                error: 'Please enter values with at most 3 decimal places for percentages and CGPA.'
            };
        }

        return { isValid: true };
    }

    /**
     * Show message
     * @param {string} message
     * @param {string} type - 'success' | 'error' | 'info'
     */
    showMessage(message, type = 'info') {
        if (!this.formMessage) return;

        this.formMessage.textContent = message;
        this.formMessage.className = 'mt-4 p-3 rounded-lg text-center block border';

        switch (type) {
            case 'success':
                this.formMessage.className += ' text-gray-700 bg-gray-100 border-gray-300';
                break;
            case 'error':
                this.formMessage.className += ' text-red-700 bg-red-100 border-red-300';
                break;
            default:
                this.formMessage.className += ' text-gray-700 bg-gray-100 border-gray-300';
        }
    }

    /**
     * Clear message
     */
    clearMessage() {
        if (this.formMessage) {
            this.formMessage.textContent = '';
            this.formMessage.className = 'mt-4 p-3 rounded-lg text-center hidden';
        }
    }

    /**
     * Reset form
     */
    reset() {
        if (this.form) {
            this.form.reset();
        }
        this.clearMessage();
    }
}

