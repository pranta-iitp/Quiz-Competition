-- Enhanced Quiz Competition Database Schema for Data Science
-- ===========================================================

-- Drop existing tables if they exist (in correct order due to dependencies)
DROP TABLE IF EXISTS table_question_feedback CASCADE;
DROP TABLE IF EXISTS table_quiz_feedback CASCADE;
DROP TABLE IF EXISTS table_learning_progress CASCADE;
DROP TABLE IF EXISTS table_quiz_events CASCADE;
DROP TABLE IF EXISTS table_user_sessions CASCADE;
DROP TABLE IF EXISTS table_participant_answer CASCADE;
DROP TABLE IF EXISTS table_quiz_attempt CASCADE;
DROP TABLE IF EXISTS table_questions CASCADE;
DROP TABLE IF EXISTS table_quizzes CASCADE;
DROP TABLE IF EXISTS table_participants CASCADE;
DROP TABLE IF EXISTS table_authors CASCADE;
DROP TABLE IF EXISTS table_users CASCADE;
DROP TABLE IF EXISTS table_quiz_status CASCADE;
DROP TABLE IF EXISTS table_roles CASCADE;

-- Create ENUM types for better data consistency
CREATE TYPE user_role_enum AS ENUM ('admin', 'superuser', 'author', 'participant');
CREATE TYPE quiz_status_enum AS ENUM ('draft', 'active', 'inactive', 'live', 'completed', 'archived');
CREATE TYPE attempt_status_enum AS ENUM ('not_started', 'in_progress', 'completed', 'abandoned', 'expired');
CREATE TYPE difficulty_level_enum AS ENUM ('beginner', 'easy', 'medium', 'hard', 'expert');
CREATE TYPE question_type_enum AS ENUM ('mcq', 'true_false', 'fill_blank', 'essay', 'matching');
CREATE TYPE device_type_enum AS ENUM ('desktop', 'tablet', 'mobile', 'unknown');
CREATE TYPE education_level_enum AS ENUM ('high_school', 'undergraduate', 'graduate', 'postgraduate', 'professional');

-- Reference Tables
-- ================

CREATE TABLE table_roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(20) NOT NULL UNIQUE,
    role_permissions TEXT, -- JSON format for flexible permissions
    role_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE table_quiz_status (
    quiz_status_id SERIAL PRIMARY KEY,
    quiz_status_name VARCHAR(20) NOT NULL UNIQUE,
    quiz_status_remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Core User Tables
-- ================

CREATE TABLE table_users (
    user_id BIGINT PRIMARY KEY, -- timestamp-based ID
    user_name VARCHAR(50) NOT NULL UNIQUE,
    user_password VARCHAR(255) NOT NULL, -- Increased for hashed passwords
    user_email VARCHAR(100) NOT NULL UNIQUE, -- Increased size
    user_role VARCHAR(20) NOT NULL,
    user_location VARCHAR(100),
    user_timezone VARCHAR(50) DEFAULT 'UTC',
    user_device_info TEXT, -- JSON for device details
    user_preferences TEXT, -- JSON for user preferences
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP,
    login_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE table_authors (
    author_id BIGINT PRIMARY KEY, -- timestamp-based ID
    author_user_id BIGINT NOT NULL,
    author_name VARCHAR(100), -- Increased size
    author_email VARCHAR(100),
    author_bio TEXT,
    author_subject_a VARCHAR(50),
    author_subject_b VARCHAR(50),
    author_subject_c VARCHAR(50),
    author_subject_d VARCHAR(50),
    author_expertise_level VARCHAR(20) DEFAULT 'intermediate',
    author_rating DECIMAL(3,2) DEFAULT 0.00, -- Average rating from participants
    total_quizzes_created INTEGER DEFAULT 0,
    total_questions_created INTEGER DEFAULT 0,
    years_of_experience INTEGER,
    certification_details TEXT, -- JSON format
    social_links TEXT, -- JSON format
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_authors_users_user_id
        FOREIGN KEY (author_user_id)
        REFERENCES table_users(user_id)
        ON DELETE CASCADE
);

CREATE TABLE table_participants (
    participant_id BIGINT PRIMARY KEY, -- timestamp-based ID
    participant_user_id BIGINT NOT NULL,
    participant_name VARCHAR(100), -- Increased size
    participant_email VARCHAR(100),
    participant_age INTEGER,
    participant_gender VARCHAR(20),
    participant_education_level VARCHAR(50),
    participant_occupation VARCHAR(100),
    participant_experience_years INTEGER,
    preferred_subject_a VARCHAR(50),
    preferred_subject_b VARCHAR(50),
    preferred_subject_c VARCHAR(50),
    preferred_subject_d VARCHAR(50),
    learning_style VARCHAR(50), -- Visual, Auditory, Kinesthetic, etc.
    learning_goals TEXT, -- JSON array
    skill_level VARCHAR(20) DEFAULT 'beginner',
    total_quizzes_attempted INTEGER DEFAULT 0,
    total_quizzes_completed INTEGER DEFAULT 0,
    average_score DECIMAL(5,2) DEFAULT 0.00,
    preferred_difficulty VARCHAR(20) DEFAULT 'medium',
    time_zone VARCHAR(50) DEFAULT 'UTC',
    language_preference VARCHAR(10) DEFAULT 'en',
    accessibility_needs TEXT, -- JSON format
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_participants_users_user_id
        FOREIGN KEY (participant_user_id)
        REFERENCES table_users(user_id)
        ON DELETE CASCADE
);

-- Quiz and Question Tables
-- ========================

CREATE TABLE table_quizzes (
    quiz_id BIGINT PRIMARY KEY,
    quiz_title VARCHAR(200) NOT NULL, -- Increased size
    quiz_description TEXT,
    quiz_subject VARCHAR(50) NOT NULL,
    quiz_category VARCHAR(50),
    quiz_tags TEXT, -- JSON array for flexible tagging
    quiz_author_id BIGINT NOT NULL,
    quiz_author_name VARCHAR(100),
    quiz_num_questions INTEGER NOT NULL,
    quiz_marks_per_question DECIMAL(5,2) NOT NULL,
    quiz_total_marks DECIMAL(8,2) GENERATED ALWAYS AS (quiz_num_questions * quiz_marks_per_question) STORED,
    quiz_negative_marks DECIMAL(5,2) DEFAULT 0.0,
    quiz_passing_marks DECIMAL(8,2),
    quiz_status VARCHAR(20) NOT NULL DEFAULT 'draft',
    quiz_difficulty_level VARCHAR(20) DEFAULT 'medium',
    quiz_duration INTEGER DEFAULT 60, -- Duration in minutes
    quiz_time_per_question INTEGER, -- Suggested time per question in seconds
    quiz_start_time TIMESTAMP,
    quiz_end_time TIMESTAMP,
    quiz_registration_deadline TIMESTAMP,
    allow_multiple_attempts BOOLEAN DEFAULT FALSE,
    max_attempts INTEGER DEFAULT 1,
    randomize_questions BOOLEAN DEFAULT FALSE,
    randomize_options BOOLEAN DEFAULT FALSE,
    show_results_immediately BOOLEAN DEFAULT TRUE,
    allow_review BOOLEAN DEFAULT TRUE,
    require_approval BOOLEAN DEFAULT FALSE,
    is_public BOOLEAN DEFAULT TRUE,
    quiz_instructions TEXT,
    quiz_image_url VARCHAR(500),
    quiz_views INTEGER DEFAULT 0,
    quiz_attempts INTEGER DEFAULT 0,
    quiz_completions INTEGER DEFAULT 0,
    quiz_average_score DECIMAL(5,2) DEFAULT 0.00,
    quiz_average_time INTEGER, -- Average completion time in minutes
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_quizzes_users
        FOREIGN KEY (quiz_author_id)
        REFERENCES table_users(user_id)
        ON DELETE SET NULL
);

CREATE TABLE table_questions (
    question_id BIGINT PRIMARY KEY,
    question_quiz_id BIGINT NOT NULL,
    question_author_id BIGINT NOT NULL,
    question_number INTEGER NOT NULL, -- Order of question in quiz
    question_question_text TEXT NOT NULL,
    question_type VARCHAR(20) DEFAULT 'mcq',
    question_option_a VARCHAR(200),
    question_option_b VARCHAR(200),
    question_option_c VARCHAR(200),
    question_option_d VARCHAR(200),
    question_option_e VARCHAR(200), -- Additional option
    question_options_count INTEGER DEFAULT 4,
    question_mark DECIMAL(5,2) NOT NULL,
    question_negative_mark DECIMAL(5,2) DEFAULT 0.0,
    question_difficulty_level VARCHAR(20) DEFAULT 'medium',
    question_category VARCHAR(50),
    question_tags TEXT, -- JSON array
    question_image_url VARCHAR(500),
    question_explanation TEXT, -- Explanation for correct answer
    question_reference_links TEXT, -- JSON array of reference URLs
    question_time_limit INTEGER, -- Time limit for this question in seconds
    questions_attempted INTEGER DEFAULT 0,
    questions_attempted_correct INTEGER DEFAULT 0,
    questions_attempted_wrong INTEGER DEFAULT 0,
    questions_skipped INTEGER DEFAULT 0,
    question_success_rate DECIMAL(5,2) GENERATED ALWAYS AS (
        CASE 
            WHEN questions_attempted > 0 
            THEN (questions_attempted_correct::DECIMAL / questions_attempted) * 100
            ELSE 0 
        END
    ) STORED,
    question_correct_option VARCHAR(5),
    question_correct_answer VARCHAR(200),
    question_is_saved BOOLEAN DEFAULT FALSE,
    question_is_approved BOOLEAN DEFAULT TRUE,
    average_time_taken DECIMAL(8,2), -- Average time taken in seconds
    question_views INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_questions_quizzes
        FOREIGN KEY (question_quiz_id)
        REFERENCES table_quizzes(quiz_id)
        ON DELETE CASCADE,
    
    CONSTRAINT fk_questions_users
        FOREIGN KEY (question_author_id)
        REFERENCES table_users(user_id)
        ON DELETE SET NULL
);

-- Quiz Attempt and Answer Tables
-- ==============================

CREATE TABLE table_quiz_attempt (
    attempt_id BIGINT PRIMARY KEY,
    attempt_quiz_id BIGINT NOT NULL,
    attempt_participant_id BIGINT NOT NULL,
    attempt_number INTEGER DEFAULT 1, -- Track multiple attempts
    attempt_start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    attempt_end_time TIMESTAMP,
    attempt_duration_minutes INTEGER,
    attempt_status VARCHAR(20) DEFAULT 'not_started',
    attempt_score DECIMAL(8,2) DEFAULT 0,
    attempt_percentage DECIMAL(5,2) DEFAULT 0,
    attempt_total_marks DECIMAL(8,2),
    attempt_passing_status BOOLEAN DEFAULT FALSE,
    correct_answers INTEGER DEFAULT 0,
    wrong_answers INTEGER DEFAULT 0,
    unanswered_questions INTEGER DEFAULT 0,
    skipped_questions INTEGER DEFAULT 0,
    questions_attempted INTEGER DEFAULT 0,
    time_per_question_avg DECIMAL(8,2), -- Average time per question
    completion_percentage DECIMAL(5,2) DEFAULT 0,
    difficulty_faced VARCHAR(20), -- Overall difficulty experienced
    participant_feedback TEXT,
    attempt_notes TEXT, -- Internal notes
    device_used VARCHAR(50),
    browser_info VARCHAR(100),
    ip_address INET,
    session_id VARCHAR(100),
    is_proctored BOOLEAN DEFAULT FALSE,
    proctor_notes TEXT,
    flags_raised INTEGER DEFAULT 0, -- Suspicious activity flags
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_quiz_attempt_quiz
        FOREIGN KEY (attempt_quiz_id)
        REFERENCES table_quizzes(quiz_id)
        ON DELETE CASCADE,
    
    CONSTRAINT fk_quiz_attempt_participant
        FOREIGN KEY (attempt_participant_id)
        REFERENCES table_participants(participant_id)
        ON DELETE CASCADE,
    
    UNIQUE(attempt_quiz_id, attempt_participant_id, attempt_number)
);

CREATE TABLE table_participant_answer (
    answer_id BIGINT PRIMARY KEY,
    attempt_id BIGINT NOT NULL,
    question_id BIGINT NOT NULL,
    question_number INTEGER NOT NULL,
    selected_answer VARCHAR(200),
    selected_option CHAR(1), -- 'A', 'B', 'C', 'D', 'E'
    correct_answer VARCHAR(200),
    correct_option CHAR(1),
    is_correct BOOLEAN DEFAULT FALSE,
    is_skipped BOOLEAN DEFAULT FALSE,
    marks_awarded DECIMAL(5,2) DEFAULT 0,
    time_taken_seconds INTEGER,
    answer_confidence_level INTEGER CHECK (answer_confidence_level >= 1 AND answer_confidence_level <= 5),
    answer_changed BOOLEAN DEFAULT FALSE,
    previous_answer VARCHAR(200),
    number_of_changes INTEGER DEFAULT 0,
    first_answer_time TIMESTAMP,
    final_answer_time TIMESTAMP,
    answer_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    answer_sequence INTEGER, -- Order in which questions were answered
    time_spent_reading INTEGER, -- Time before first interaction
    hint_used BOOLEAN DEFAULT FALSE,
    flag_for_review BOOLEAN DEFAULT FALSE,
    participant_notes TEXT,
    
    CONSTRAINT fk_participant_answer_attempt
        FOREIGN KEY (attempt_id)
        REFERENCES table_quiz_attempt(attempt_id)
        ON DELETE CASCADE,
    
    CONSTRAINT fk_participant_answer_question
        FOREIGN KEY (question_id)
        REFERENCES table_questions(question_id)
        ON DELETE CASCADE,
    
    UNIQUE(attempt_id, question_id)
);

-- Analytics and Tracking Tables
-- =============================

CREATE TABLE table_user_sessions (
    session_id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_end TIMESTAMP,
    session_duration_minutes INTEGER,
    pages_visited INTEGER DEFAULT 0,
    actions_performed INTEGER DEFAULT 0,
    quizzes_viewed INTEGER DEFAULT 0,
    quizzes_attempted INTEGER DEFAULT 0,
    device_type VARCHAR(50),
    device_model VARCHAR(100),
    browser_info VARCHAR(100),
    operating_system VARCHAR(50),
    screen_resolution VARCHAR(20),
    ip_address INET,
    location_country VARCHAR(50),
    location_city VARCHAR(50),
    referrer_url VARCHAR(500),
    user_agent TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_user_sessions_user
        FOREIGN KEY (user_id)
        REFERENCES table_users(user_id)
        ON DELETE CASCADE
);

CREATE TABLE table_quiz_events (
    event_id BIGINT PRIMARY KEY,
    session_id BIGINT,
    attempt_id BIGINT,
    user_id BIGINT NOT NULL,
    quiz_id BIGINT,
    question_id BIGINT,
    event_type VARCHAR(50) NOT NULL, -- 'quiz_started', 'question_viewed', 'answer_selected', 'answer_changed', 'question_skipped', 'quiz_submitted', etc.
    event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    event_data TEXT, -- JSON for additional event details
    page_url VARCHAR(500),
    time_spent_seconds INTEGER,
    scroll_depth DECIMAL(5,2), -- Percentage of page scrolled
    click_coordinates VARCHAR(20), -- x,y coordinates
    device_orientation VARCHAR(20), -- portrait, landscape
    network_type VARCHAR(20), -- wifi, cellular, etc.
    
    CONSTRAINT fk_quiz_events_user
        FOREIGN KEY (user_id)
        REFERENCES table_users(user_id)
        ON DELETE CASCADE,
    
    CONSTRAINT fk_quiz_events_session
        FOREIGN KEY (session_id)
        REFERENCES table_user_sessions(session_id)
        ON DELETE SET NULL,
    
    CONSTRAINT fk_quiz_events_attempt
        FOREIGN KEY (attempt_id)
        REFERENCES table_quiz_attempt(attempt_id)
        ON DELETE CASCADE
);

CREATE TABLE table_learning_progress (
    progress_id BIGINT PRIMARY KEY,
    participant_id BIGINT NOT NULL,
    subject VARCHAR(50) NOT NULL,
    topic VARCHAR(100),
    skill_level VARCHAR(20) DEFAULT 'beginner',
    progress_percentage DECIMAL(5,2) DEFAULT 0.00,
    mastery_level DECIMAL(5,2) DEFAULT 0.00, -- 0-100 scale
    time_spent_hours DECIMAL(8,2) DEFAULT 0.00,
    quizzes_completed INTEGER DEFAULT 0,
    average_score DECIMAL(5,2) DEFAULT 0.00,
    best_score DECIMAL(5,2) DEFAULT 0.00,
    improvement_rate DECIMAL(5,2) DEFAULT 0.00, -- Percentage improvement over time
    strengths TEXT, -- JSON array of strong topics
    weaknesses TEXT, -- JSON array of weak topics
    recommended_topics TEXT, -- JSON array of recommended study topics
    learning_path TEXT, -- JSON array of suggested learning sequence
    last_quiz_date TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    next_milestone VARCHAR(100),
    estimated_time_to_mastery INTEGER, -- Hours
    
    CONSTRAINT fk_learning_progress_participant
        FOREIGN KEY (participant_id)
        REFERENCES table_participants(participant_id)
        ON DELETE CASCADE,
    
    UNIQUE(participant_id, subject, topic)
);

-- Feedback and Rating Tables
-- ==========================

CREATE TABLE table_quiz_feedback (
    feedback_id BIGINT PRIMARY KEY,
    quiz_id BIGINT NOT NULL,
    participant_id BIGINT NOT NULL,
    attempt_id BIGINT,
    overall_rating INTEGER CHECK (overall_rating >= 1 AND overall_rating <= 5),
    difficulty_rating INTEGER CHECK (difficulty_rating >= 1 AND difficulty_rating <= 5),
    content_quality_rating INTEGER CHECK (content_quality_rating >= 1 AND content_quality_rating <= 5),
    user_experience_rating INTEGER CHECK (user_experience_rating >= 1 AND user_experience_rating <= 5),
    time_adequacy_rating INTEGER CHECK (time_adequacy_rating >= 1 AND time_adequacy_rating <= 5),
    would_recommend BOOLEAN,
    comments TEXT,
    suggestions TEXT,
    technical_issues TEXT,
    favorite_aspects TEXT,
    least_favorite_aspects TEXT,
    completion_satisfaction INTEGER CHECK (completion_satisfaction >= 1 AND completion_satisfaction <= 5),
    feedback_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_anonymous BOOLEAN DEFAULT FALSE,
    helpful_votes INTEGER DEFAULT 0,
    
    CONSTRAINT fk_quiz_feedback_quiz
        FOREIGN KEY (quiz_id)
        REFERENCES table_quizzes(quiz_id)
        ON DELETE CASCADE,
    
    CONSTRAINT fk_quiz_feedback_participant
        FOREIGN KEY (participant_id)
        REFERENCES table_participants(participant_id)
        ON DELETE CASCADE,
    
    CONSTRAINT fk_quiz_feedback_attempt
        FOREIGN KEY (attempt_id)
        REFERENCES table_quiz_attempt(attempt_id)
        ON DELETE CASCADE,
    
    UNIQUE(quiz_id, participant_id, attempt_id)
);

CREATE TABLE table_question_feedback (
    feedback_id BIGINT PRIMARY KEY,
    question_id BIGINT NOT NULL,
    participant_id BIGINT NOT NULL,
    attempt_id BIGINT,
    is_unclear BOOLEAN DEFAULT FALSE,
    is_too_difficult BOOLEAN DEFAULT FALSE,
    is_too_easy BOOLEAN DEFAULT FALSE,
    has_errors BOOLEAN DEFAULT FALSE,
    clarity_rating INTEGER CHECK (clarity_rating >= 1 AND clarity_rating <= 5),
    relevance_rating INTEGER CHECK (relevance_rating >= 1 AND relevance_rating <= 5),
    suggested_improvement TEXT,
    alternative_wording TEXT,
    additional_options TEXT,
    explanation_needed BOOLEAN DEFAULT FALSE,
    flag_inappropriate BOOLEAN DEFAULT FALSE,
    comments TEXT,
    feedback_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_question_feedback_question
        FOREIGN KEY (question_id)
        REFERENCES table_questions(question_id)
        ON DELETE CASCADE,
    
    CONSTRAINT fk_question_feedback_participant
        FOREIGN KEY (participant_id)
        REFERENCES table_participants(participant_id)
        ON DELETE CASCADE,
    
    CONSTRAINT fk_question_feedback_attempt
        FOREIGN KEY (attempt_id)
        REFERENCES table_quiz_attempt(attempt_id)
        ON DELETE CASCADE
);

-- Performance Optimization Indexes
-- =================================

-- User-related indexes
CREATE INDEX idx_users_email ON table_users(user_email);
CREATE INDEX idx_users_role ON table_users(user_role);
CREATE INDEX idx_users_active ON table_users(is_active);
CREATE INDEX idx_users_last_login ON table_users(last_login);

-- Quiz-related indexes
CREATE INDEX idx_quizzes_subject ON table_quizzes(quiz_subject);
CREATE INDEX idx_quizzes_status ON table_quizzes(quiz_status);
CREATE INDEX idx_quizzes_author ON table_quizzes(quiz_author_id);
CREATE INDEX idx_quizzes_public ON table_quizzes(is_public);
CREATE INDEX idx_quizzes_created ON table_quizzes(created_at);
CREATE INDEX idx_quizzes_difficulty ON table_quizzes(quiz_difficulty_level);

-- Question-related indexes
CREATE INDEX idx_questions_quiz ON table_questions(question_quiz_id);
CREATE INDEX idx_questions_difficulty ON table_questions(question_difficulty_level);
CREATE INDEX idx_questions_category ON table_questions(question_category);
CREATE INDEX idx_questions_success_rate ON table_questions(question_success_rate);

-- Attempt-related indexes
CREATE INDEX idx_attempts_participant ON table_quiz_attempt(attempt_participant_id);
CREATE INDEX idx_attempts_quiz ON table_quiz_attempt(attempt_quiz_id);
CREATE INDEX idx_attempts_status ON table_quiz_attempt(attempt_status);
CREATE INDEX idx_attempts_date ON table_quiz_attempt(attempt_start_time);
CREATE INDEX idx_attempts_score ON table_quiz_attempt(attempt_score);

-- Answer-related indexes
CREATE INDEX idx_answers_attempt ON table_participant_answer(attempt_id);
CREATE INDEX idx_answers_question ON table_participant_answer(question_id);
CREATE INDEX idx_answers_correct ON table_participant_answer(is_correct);
CREATE INDEX idx_answers_time ON table_participant_answer(time_taken_seconds);

-- Analytics indexes
CREATE INDEX idx_sessions_user ON table_user_sessions(user_id);
CREATE INDEX idx_sessions_active ON table_user_sessions(is_active);
CREATE INDEX idx_sessions_start ON table_user_sessions(session_start);

CREATE INDEX idx_events_user ON table_quiz_events(user_id);
CREATE INDEX idx_events_type ON table_quiz_events(event_type);
CREATE INDEX idx_events_timestamp ON table_quiz_events(event_timestamp);
CREATE INDEX idx_events_quiz ON table_quiz_events(quiz_id);

CREATE INDEX idx_progress_participant ON table_learning_progress(participant_id);
CREATE INDEX idx_progress_subject ON table_learning_progress(subject);
CREATE INDEX idx_progress_level ON table_learning_progress(skill_level);

-- Composite indexes for common queries
CREATE INDEX idx_quiz_attempt_participant_quiz ON table_quiz_attempt(attempt_participant_id, attempt_quiz_id);
CREATE INDEX idx_participant_answer_attempt_question ON table_participant_answer(attempt_id, question_id);
CREATE INDEX idx_questions_quiz_difficulty ON table_questions(question_quiz_id, question_difficulty_level);
CREATE INDEX idx_quizzes_subject_status ON table_quizzes(quiz_subject, quiz_status);

-- Insert default reference data
-- =============================

INSERT INTO table_roles (role_name, role_permissions, role_description) VALUES
('admin', '{"all": true}', 'System administrator with full access'),
('superuser', '{"manage_users": true, "manage_content": true, "view_analytics": true}', 'Super user with elevated privileges'),
('author', '{"create_quiz": true, "manage_own_content": true, "view_own_analytics": true}', 'Quiz creator and content author'),
('participant', '{"take_quiz": true, "view_own_results": true}', 'Quiz participant with basic access');

INSERT INTO table_quiz_status (quiz_status_name, quiz_status_remarks) VALUES
('draft', 'Quiz is being created and not yet published'),
('active', 'Quiz is published and available for participants'),
('inactive', 'Quiz is temporarily disabled'),
('live', 'Quiz is currently running with time constraints'),
('completed', 'Quiz has ended and no longer accepting submissions'),
('archived', 'Quiz has been archived for historical reference');

-- Views for Common Analytics Queries
-- ==================================

CREATE VIEW view_participant_performance AS
SELECT 
    p.participant_id,
    p.participant_name,
    p.participant_email,
    COUNT(qa.attempt_id) as total_attempts,
    COUNT(CASE WHEN qa.attempt_status = 'completed' THEN 1 END) as completed_attempts,
    AVG(qa.attempt_score) as average_score,
    MAX(qa.attempt_score) as best_score,
    AVG(qa.attempt_duration_minutes) as average_duration,
    COUNT(DISTINCT qa.attempt_quiz_id) as unique_quizzes_attempted,
    MIN(qa.attempt_start_time) as first_attempt_date,
    MAX(qa.attempt_start_time) as last_attempt_date
FROM table_participants p
LEFT JOIN table_quiz_attempt qa ON p.participant_id = qa.attempt_participant_id
GROUP BY p.participant_id, p.participant_name, p.participant_email;

CREATE VIEW view_quiz_analytics AS
SELECT 
    q.quiz_id,
    q.quiz_title,
    q.quiz_subject,
    q.quiz_difficulty_level,
    COUNT(qa.attempt_id) as total_attempts,
    COUNT(CASE WHEN qa.attempt_status = 'completed' THEN 1 END) as completed_attempts,
    AVG(qa.attempt_score) as average_score,
    AVG(qa.attempt_duration_minutes) as average_duration,
    COUNT(DISTINCT qa.attempt_participant_id) as unique_participants,
    (COUNT(CASE WHEN qa.attempt_status = 'completed' THEN 1 END)::DECIMAL / 
     NULLIF(COUNT(qa.attempt_id), 0) * 100) as completion_rate
FROM table_quizzes q
LEFT JOIN table_quiz_attempt qa ON q.quiz_id = qa.attempt_quiz_id
GROUP BY q.quiz_id, q.quiz_title, q.quiz_subject, q.quiz_difficulty_level;

CREATE VIEW view_question_difficulty_analysis AS
SELECT 
    qu.question_id,
    qu.question_quiz_id,
    qu.question_difficulty_level,
    qu.questions_attempted,
    qu.questions_attempted_correct,
    qu.question_success_rate,
    AVG(pa.time_taken_seconds) as avg_time_taken,
    COUNT(CASE WHEN pa.answer_changed = true THEN 1 END) as times_changed,
    COUNT(CASE WHEN pa.is_skipped = true THEN 1 END) as times_skipped
FROM table_questions qu
LEFT JOIN table_participant_answer pa ON qu.question_id = pa.question_id
GROUP BY qu.question_id, qu.question_quiz_id, qu.question_difficulty_level, 
         qu.questions_attempted, qu.questions_attempted_correct, qu.question_success_rate;

-- Triggers for Data Consistency
-- =============================

-- Update quiz statistics when attempts are made
CREATE OR REPLACE FUNCTION update_quiz_stats()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        UPDATE table_quizzes 
        SET 
            quiz_attempts = (SELECT COUNT(*) FROM table_quiz_attempt WHERE attempt_quiz_id = NEW.attempt_quiz_id),
            quiz_completions = (SELECT COUNT(*) FROM table_quiz_attempt WHERE attempt_quiz_id = NEW.attempt_quiz_id AND attempt_status = 'completed'),
            quiz_average_score = (SELECT AVG(attempt_score) FROM table_quiz_attempt WHERE attempt_quiz_id = NEW.attempt_quiz_id AND attempt_status = 'completed'),
            updated_at = CURRENT_TIMESTAMP
        WHERE quiz_id = NEW.attempt_quiz_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_quiz_stats
    AFTER INSERT OR UPDATE ON table_quiz_attempt
    FOR EACH ROW EXECUTE FUNCTION update_quiz_stats();

-- Update question statistics when answers are submitted
CREATE OR REPLACE FUNCTION update_question_stats()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        UPDATE table_questions 
        SET 
            questions_attempted = (SELECT COUNT(*) FROM table_participant_answer WHERE question_id = NEW.question_id AND is_skipped = false),
            questions_attempted_correct = (SELECT COUNT(*) FROM table_participant_answer WHERE question_id = NEW.question_id AND is_correct = true),
            questions_attempted_wrong = (SELECT COUNT(*) FROM table_participant_answer WHERE question_id = NEW.question_id AND is_correct = false AND is_skipped = false),
            questions_skipped = (SELECT COUNT(*) FROM table_participant_answer WHERE question_id = NEW.question_id AND is_skipped = true),
            average_time_taken = (SELECT AVG(time_taken_seconds) FROM table_participant_answer WHERE question_id = NEW.question_id AND is_skipped = false),
            updated_at = CURRENT_TIMESTAMP
        WHERE question_id = NEW.question_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_question_stats
    AFTER INSERT OR UPDATE ON table_participant_answer
    FOR EACH ROW EXECUTE FUNCTION update_question_stats();

-- Comments for Documentation
-- =========================
COMMENT ON DATABASE current_database() IS 'Enhanced Quiz Competition Database with Data Science Analytics Capabilities';
COMMENT ON TABLE table_users IS 'Core user information with authentication and profile data';
COMMENT ON TABLE table_quiz_attempt IS 'Individual quiz attempts with detailed performance metrics';
COMMENT ON TABLE table_participant_answer IS 'Individual question responses with timing and behavior data';
COMMENT ON TABLE table_quiz_events IS 'Detailed event tracking for user behavior analysis';
COMMENT ON TABLE table_learning_progress IS 'Learning analytics and progress tracking per participant';
COMMENT ON VIEW view_participant_performance IS 'Aggregated participant performance metrics for dashboards';
COMMENT ON VIEW view_quiz_analytics IS 'Quiz-level analytics including completion rates and scores';