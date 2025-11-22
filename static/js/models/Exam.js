/**
 * Exam Model - Represents an exam with eligibility criteria
 */
export class Exam {
    constructor(data) {
        this.examId = data.exam_id || data.examId;
        this.examName = data.exam_name || data.examName;
        this.conductingBody = data.conducting_body || data.conductingBody;
        this.examLevel = data.exam_level || data.examLevel;
        this.examMode = data.exam_mode || data.examMode;
        this.website = data.website;
        this.feeGenEws = data.fee_gen_ews || data.feeGenEws;
        this.totalDurationMins = data.total_duration_mins || data.totalDurationMins;
        this.minAge = data.min_age || data.minAge;
        this.maxAge = data.max_age || data.maxAge;
        this.min10Percent = data.min_10_percent || data.min10Percent;
        this.min12Percent = data.min_12_percent || data.min12Percent;
        this.minUgCgpa = data.min_ug_cgpa || data.minUgCgpa;
        this.subjects = data.subjects || [];
        this.documents = data.documents || [];
    }

    /**
     * Check if a candidate is eligible for this exam
     * @param {Candidate} candidate - Candidate to check
     * @returns {boolean}
     */
    isEligible(candidate) {
        // Age check
        if (candidate.age < this.minAge || candidate.age > this.maxAge) {
            return false;
        }

        // Academic checks
        if (candidate.p10 < this.min10Percent) {
            return false;
        }

        if (candidate.p12 < this.min12Percent) {
            return false;
        }

        if (candidate.ugCgpa < this.minUgCgpa) {
            return false;
        }

        return true;
    }

    /**
     * Convert to plain object
     * @returns {Object}
     */
    toObject() {
        return {
            exam_id: this.examId,
            exam_name: this.examName,
            conducting_body: this.conductingBody,
            exam_level: this.examLevel,
            exam_mode: this.examMode,
            website: this.website,
            fee_gen_ews: this.feeGenEws,
            total_duration_mins: this.totalDurationMins,
            min_age: this.minAge,
            max_age: this.maxAge,
            min_10_percent: this.min10Percent,
            min_12_percent: this.min12Percent,
            min_ug_cgpa: this.minUgCgpa,
            subjects: this.subjects,
            documents: this.documents
        };
    }
}

