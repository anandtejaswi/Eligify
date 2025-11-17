// ELIGIFY Node.js Backend Server (Conceptual)
// NOTE: This file is conceptual and cannot be executed in this environment.

const express = require('express');
const mysql = require('mysql');
const bodyParser = require('body-parser');

const app = express();
const port = 3000;

// Configuration for MySQL Connection
const db = mysql.createConnection({
    host: 'localhost',
    user: 'your_mysql_user', // CHANGE THIS
    password: 'your_mysql_password', // CHANGE THIS
    database: 'eligify_db'
});

db.connect(err => {
    if (err) {
        console.error('Error connecting to MySQL: ' + err.stack);
        return;
    }
    console.log('Connected to MySQL as id ' + db.threadId);
});

// Middleware
app.use(bodyParser.json());
// Serve static files (like your index.html)
app.use(express.static(__dirname)); 

// -----------------------------------------------------------------
// API Endpoint 1: Register Candidate
// -----------------------------------------------------------------
app.post('/api/register', (req, res) => {
    const candidateData = req.body;

    // The actual query to insert data into the Candidate table
    const sql = 'INSERT INTO Candidate SET ?';
    db.query(sql, candidateData, (err, result) => {
        if (err) {
            console.error(err);
            return res.status(500).json({ error: 'Database insertion failed.' });
        }
        const candidateId = result.insertId;
        
        // This is where you would call the eligibility check function
        // For a real app, you would fetch all exam data and run the matching logic here.
        // For now, we simulate success:
        res.json({ 
            message: 'Registration successful!', 
            candidateId: candidateId,
            status: 'Proceed to eligibility check.'
        });
    });
});

// -----------------------------------------------------------------
// API Endpoint 2: Get Eligible Exams (The core logic)
// -----------------------------------------------------------------
app.post('/api/eligibility', (req, res) => {
    const candidate = req.body;

    // 1. Fetch all Exam details, Eligibility, Subjects, etc., using JOINs
    const sql = `
        SELECT *
        FROM Exam e
        JOIN Eligibility el ON e.exam_id = el.exam_id
        JOIN Subjects s ON e.exam_id = s.exam_id
        JOIN Documents d ON e.exam_id = d.exam_id
        JOIN Reservation r ON e.exam_id = r.exam_id;
    `;

    db.query(sql, (err, exams) => {
        if (err) return res.status(500).json({ error: 'Failed to fetch exam data.' });

        const eligibleExams = exams.filter(exam => {
            // MATCHING LOGIC (Similar to the one in index.html):
            const isAgeEligible = candidate.age >= exam.min_age && candidate.age <= exam.max_age;
            const is10thEligible = candidate.p_10 >= exam.min_10_percent;
            const is12thEligible = candidate.p_12 >= exam.min_12_percent;
            const isUGCGPAEligible = candidate.ug_cgpa >= exam.min_ug_cgpa;

            return isAgeEligible && is10thEligible && is12thEligible && isUGCGPAEligible;
        });

        res.json({ eligibleExams });
    });
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});