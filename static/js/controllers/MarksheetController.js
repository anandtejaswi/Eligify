/**
 * Marksheet Controller - Handles marksheet scanning interactions
 */
import { MarksheetScannerView } from '../views/MarksheetScannerView.js';
import { ApiService } from '../services/ApiService.js';

export class MarksheetController {
    constructor() {
        this.view = new MarksheetScannerView();
        this.apiService = new ApiService();
        this.init();
    }

    /**
     * Initialize event listeners
     */
    init() {
        if (this.view.scanButton) {
            this.view.scanButton.addEventListener('click', () => this.handleScan());
        }
    }

    /**
     * Handle scan button click
     */
    async handleScan() {
        const formData = this.view.getFormData();

        // Validate file
        if (!formData.file) {
            this.view.showMessage('Please select a PDF file.', 'error');
            return;
        }

        // Clear previous results
        this.view.clearResults();
        this.view.setLoading(true);

        try {
            // Call API
            const result = await this.apiService.parseMarksheet(
                formData.file,
                formData.method,
                formData.dpi
            );

            // Check for errors in response
            if (result.fields && result.fields.error) {
                this.view.showMessage(result.fields.error, 'warning');
                return;
            }

            // Display results
            if (result.fields) {
                this.view.displayResults(result.fields);
                this.view.showMessage('Marksheet scanned successfully!', 'success');
            } else {
                this.view.showMessage('No data extracted from marksheet.', 'warning');
            }
        } catch (error) {
            this.view.showMessage(error.message || 'Network or server error.', 'error');
        } finally {
            this.view.setLoading(false);
        }
    }
}

