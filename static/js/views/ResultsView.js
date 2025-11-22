/**
 * Results View - Handles display of eligibility results
 */
import { escapeHtml } from '../utils/security.js';
import { Exam } from '../models/Exam.js';

export class ResultsView {
    constructor() {
        this.container = document.getElementById('results-container');
        this.initialMessage = document.getElementById('initial-message');
    }

    /**
     * Render exam card
     * @param {Exam} exam
     * @returns {string} HTML string
     */
    renderExamCard(exam) {
        const fee = `${escapeHtml(exam.feeGenEws)} INR (GEN/EWS)`;
        const subjectsHtml = exam.subjects.map(s => 
            `<span class="inline-block bg-gray-200 text-gray-800 text-xs px-2 py-1 rounded-full">${escapeHtml(s)}</span>`
        ).join(' ');
        const docsHtml = exam.documents.map(d => 
            `<li class="text-sm text-gray-700">${escapeHtml(d)}</li>`
        ).join('');

        // Validate and escape website URL
        let websiteUrl = escapeHtml(exam.website);
        if (!websiteUrl.match(/^https?:\/\//i)) {
            websiteUrl = 'https://' + websiteUrl;
        }

        return `
            <div class="bg-gray-100 border-l-4 border-gray-900 p-4 rounded-lg shadow-md hover:shadow-lg transition duration-300">
                <h3 class="text-xl font-bold text-gray-900">
                    <a href="${escapeHtml(websiteUrl)}" target="_blank" rel="noopener noreferrer" class="hover:underline text-gray-900">
                        ${escapeHtml(exam.examName)}
                    </a>
                </h3>
                <p class="text-sm text-gray-500 mb-3">${escapeHtml(exam.conductingBody)} | Level: ${escapeHtml(exam.examLevel)}</p>
                
                <div class="space-y-3">
                    <p class="text-gray-700"><span class="font-semibold">Mode:</span> ${escapeHtml(exam.examMode)}</p>
                    <p class="text-gray-700"><span class="font-semibold">Duration:</span> ${escapeHtml(exam.totalDurationMins)} mins</p>
                    <p class="text-gray-700"><span class="font-semibold">Fees (Approx):</span> ${fee}</p>
                </div>

                <div class="mt-4">
                    <p class="font-semibold text-gray-800">Key Subjects:</p>
                    <div class="flex flex-wrap gap-2 mt-1">${subjectsHtml}</div>
                </div>

                <div class="mt-4">
                    <p class="font-semibold text-gray-800">Documents Required:</p>
                    <ul class="list-disc list-inside ml-2 text-sm">${docsHtml}</ul>
                </div>
            </div>
        `;
    }

    /**
     * Display eligible exams
     * @param {Exam[]} exams
     */
    displayExams(exams) {
        if (!this.container) return;

        this.container.innerHTML = '';

        if (exams.length === 0) {
            this.showNoResults();
            return;
        }

        exams.forEach(exam => {
            this.container.innerHTML += this.renderExamCard(exam);
        });

        // Scroll to results
        this.container.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    /**
     * Show no results message
     * @param {Object} candidate - Candidate data for context
     */
    showNoResults(candidate = null) {
        if (!this.container) return;

        let message = 'No exams found matching your criteria.';
        if (candidate) {
            message = `No exams found matching the criteria: Age (${escapeHtml(String(candidate.age))}), 10th% (${escapeHtml(String(candidate.p10))}), 12th% (${escapeHtml(String(candidate.p12))}), UG CGPA (${escapeHtml(String(candidate.ugCgpa))}). Try adjusting your profile data.`;
        }

        this.container.innerHTML = `
            <p class="text-center text-gray-500 p-10 bg-gray-50 rounded-lg border border-gray-200">
                ${message}
            </p>
        `;
    }

    /**
     * Show initial message
     */
    showInitialMessage() {
        if (!this.container) return;
        this.container.innerHTML = `
            <p id="initial-message" class="text-center text-gray-500 p-10 bg-gray-50 rounded-lg">
                Please fill out the form to check your eligibility against our mock database of exams.
            </p>
        `;
    }

    /**
     * Clear results
     */
    clear() {
        if (this.container) {
            this.container.innerHTML = '';
        }
        this.showInitialMessage();
    }
}

