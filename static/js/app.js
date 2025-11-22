/**
 * Main Application Entry Point
 * Initializes all controllers and services
 */
import { MOCK_EXAM_DB } from './data/exams.js';
import { ExamService } from './services/ExamService.js';
import { CandidateController } from './controllers/CandidateController.js';
import { MarksheetController } from './controllers/MarksheetController.js';

/**
 * Initialize the application
 */
function init() {
    // Initialize exam service with mock data
    const examService = new ExamService(MOCK_EXAM_DB);

    // Initialize controllers
    const candidateController = new CandidateController(examService);
    const marksheetController = new MarksheetController();

    console.log('ELIGIFY application initialized');
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

