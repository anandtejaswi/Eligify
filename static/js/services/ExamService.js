/**
 * Exam Service - Business logic for exam eligibility checking
 */
import { Exam } from '../models/Exam.js';

export class ExamService {
    constructor(exams) {
        this.exams = exams.map(examData => new Exam(examData));
    }

    /**
     * Check which exams a candidate is eligible for
     * @param {Candidate} candidate - Candidate to check
     * @returns {Exam[]} Array of eligible exams
     */
    checkEligibility(candidate) {
        return this.exams.filter(exam => exam.isEligible(candidate));
    }

    /**
     * Get all exams
     * @returns {Exam[]}
     */
    getAllExams() {
        return this.exams;
    }

    /**
     * Get exam by ID
     * @param {number} examId
     * @returns {Exam|null}
     */
    getExamById(examId) {
        return this.exams.find(exam => exam.examId === examId) || null;
    }
}

