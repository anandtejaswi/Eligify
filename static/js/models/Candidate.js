/**
 * Candidate Model - Represents a candidate with validation
 */
export class Candidate {
    constructor(data) {
        this.firstName = data.firstName || '';
        this.dob = data.dob || '';
        this.email = data.email || '';
        this.category = data.category || '';
        this.p10 = parseFloat(data.p10) || 0;
        this.p12 = parseFloat(data.p12) || 0;
        this.ugCgpa = parseFloat(data.ugCgpa) || 0;
        this.age = this.calculateAge(this.dob);
    }

    /**
     * Calculates the current age based on the date of birth.
     * @param {string} dob - Date of Birth string (YYYY-MM-DD).
     * @returns {number} The current age in years.
     */
    calculateAge(dob) {
        if (!dob) return 0;
        const today = new Date();
        const birthDate = new Date(dob);
        let age = today.getFullYear() - birthDate.getFullYear();
        const m = today.getMonth() - birthDate.getMonth();
        if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
            age--;
        }
        return age;
    }

    /**
     * Validates candidate data
     * @returns {Object} {isValid: boolean, errors: string[]}
     */
    validate() {
        const errors = [];

        if (!this.firstName || this.firstName.trim().length < 2) {
            errors.push('First name must be at least 2 characters');
        }

        if (!this.email || !this.email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
            errors.push('Invalid email format');
        }

        if (!this.category) {
            errors.push('Category is required');
        }

        if (this.p10 < 0 || this.p10 > 100) {
            errors.push('10th percentage must be between 0 and 100');
        }

        if (this.p12 < 0 || this.p12 > 100) {
            errors.push('12th percentage must be between 0 and 100');
        }

        if (this.ugCgpa < 0 || this.ugCgpa > 10) {
            errors.push('UG CGPA must be between 0 and 10');
        }

        if (!this.dob) {
            errors.push('Date of birth is required');
        }

        return {
            isValid: errors.length === 0,
            errors: errors
        };
    }

    /**
     * Convert to plain object
     * @returns {Object}
     */
    toObject() {
        return {
            firstName: this.firstName,
            dob: this.dob,
            email: this.email,
            category: this.category,
            p10: this.p10,
            p12: this.p12,
            ugCgpa: this.ugCgpa,
            age: this.age
        };
    }
}

