/**
 * Candidate Controller - Handles candidate form interactions
 */
import { Candidate } from '../models/Candidate.js';
import { CandidateFormView } from '../views/CandidateFormView.js';
import { ResultsView } from '../views/ResultsView.js';
import { ExamService } from '../services/ExamService.js';
import { escapeHtml, setTextContent } from '../utils/security.js';

export class CandidateController {
    constructor(examService) {
        this.examService = examService;
        this.formView = new CandidateFormView();
        this.resultsView = new ResultsView();
        this.init();
    }

    /**
     * Initialize event listeners
     */
    init() {
        if (this.formView.form) {
            this.formView.form.addEventListener('submit', (e) => this.handleSubmit(e));
        }
    }

    /**
     * Handle form submission
     * @param {Event} e
     */
    handleSubmit(e) {
        e.preventDefault();

        // Validate input
        const validation = this.formView.validateInput();
        if (!validation.isValid) {
            this.formView.showMessage(validation.error, 'error');
            return;
        }

        // Get form data
        const formData = this.formView.getFormData();

        // Create candidate model
        let candidate;
        try {
            candidate = new Candidate(formData);
            const candidateValidation = candidate.validate();
            
            if (!candidateValidation.isValid) {
                this.formView.showMessage(candidateValidation.errors.join('; '), 'error');
                return;
            }
        } catch (error) {
            this.formView.showMessage(error.message || 'Invalid candidate data', 'error');
            return;
        }

        // Check eligibility
        const eligibleExams = this.examService.checkEligibility(candidate);

        // Display results
        if (eligibleExams.length > 0) {
            const message = `Success! ${escapeHtml(candidate.firstName)}, your profile has been matched with ${eligibleExams.length} exams.`;
            this.formView.showMessage(message, 'success');
            this.resultsView.displayExams(eligibleExams);
        } else {
            const message = `Sorry, ${escapeHtml(candidate.firstName)}. No exams matched your criteria in our database.`;
            this.formView.showMessage(message, 'info');
            this.resultsView.showNoResults(candidate.toObject());
        }
    }
}

