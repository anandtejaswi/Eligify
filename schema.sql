-- ELIGIFY Database Schema
-- Run this file in your MySQL environment (e.g., MySQL Workbench or Command Line)

-- Drop database if it exists and create a new one
DROP DATABASE IF EXISTS eligify_db;
CREATE DATABASE eligify_db;
USE eligify_db;

-- -----------------------------------------------------
-- Table: Exam
-- -----------------------------------------------------
CREATE TABLE Exam (
    exam_id INT PRIMARY KEY,
    exam_name VARCHAR(100) NOT NULL,
    max_attempts INT,
    conducting_body VARCHAR(100),
    exam_level VARCHAR(100), -- E.g., National, State
    exam_mode VARCHAR(100), -- E.g., Online, Offline
    website VARCHAR(200),
    exam_month INT,
    exam_type VARCHAR(100), -- E.g., Engineering, Medical
    fee_gen_ews INT,
    total_duration_mins INT
);

-- -----------------------------------------------------
-- Table: Subjects (Linked to Exam)
-- -----------------------------------------------------
CREATE TABLE Subjects (
    exam_id INT PRIMARY KEY,
    num_subjects INT,
    subject_1 VARCHAR(200),
    subject_2 VARCHAR(200),
    subject_3 VARCHAR(200),
    subject_4 VARCHAR(200),
    FOREIGN KEY (exam_id) REFERENCES Exam(exam_id) ON DELETE CASCADE
);

-- -----------------------------------------------------
-- Table: Eligibility (Linked to Exam)
-- -----------------------------------------------------
CREATE TABLE Eligibility (
    exam_id INT PRIMARY KEY,
    min_age INT,
    max_age INT,
    min_10_percent INT,
    min_12_percent INT,
    min_ug_cgpa FLOAT,
    FOREIGN KEY (exam_id) REFERENCES Exam(exam_id) ON DELETE CASCADE
);

-- -----------------------------------------------------
-- Table: Reservation (Linked to Exam)
-- -----------------------------------------------------
CREATE TABLE Reservation (
    exam_id INT PRIMARY KEY,
    ews_percent INT,
    obc_ncl_percent INT,
    sc_percent INT,
    st_percent INT,
    FOREIGN KEY (exam_id) REFERENCES Exam(exam_id) ON DELETE CASCADE
);

-- -----------------------------------------------------
-- Table: Documents (Linked to Exam)
-- -----------------------------------------------------
CREATE TABLE Documents (
    exam_id INT PRIMARY KEY,
    caste_certificate BOOLEAN,
    domicile BOOLEAN,
    birth_certificate BOOLEAN,
    photo BOOLEAN,
    signature BOOLEAN,
    aadhar BOOLEAN,
    ug_degree BOOLEAN,
    pg_degree BOOLEAN,
    FOREIGN KEY (exam_id) REFERENCES Exam(exam_id) ON DELETE CASCADE
);

-- -----------------------------------------------------
-- Table: Candidate (The user registration table)
-- -----------------------------------------------------
CREATE TABLE Candidate (
    candidate_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    dob DATE NOT NULL,
    age INT, -- Derived/calculated field
    gender CHAR(1) CHECK (gender IN ('M', 'F', 'O')),
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    qualification VARCHAR(100),
    category VARCHAR(50),
    p_10 FLOAT, -- 10th Percentage
    p_12 FLOAT, -- 12th Percentage
    course VARCHAR(100),
    ug_cgpa FLOAT,
    pg_cgpa FLOAT
);