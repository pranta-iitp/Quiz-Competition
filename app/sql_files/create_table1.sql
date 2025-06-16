-- Create ENUM type for role
--CREATE TYPE user_predefined_role AS ENUM ('admin', 'superuser', 'author', 'participant');

CREATE TABLE table_roles (
    role_id INT PRIMARY KEY, 
    role_name VARCHAR(20) NOT NULL UNIQUE,
    role_permissions VARCHAR(250) 
);

CREATE TABLE table_quiz_status (
    quiz_status_id INT PRIMARY KEY, 
    quiz_status_name VARCHAR(20) NOT NULL UNIQUE,
    quiz_status_remarks VARCHAR(150) 
);

-- Create table
CREATE TABLE table_users (
    user_id BIGINT PRIMARY KEY,  -- will store timestamp (in milliseconds or seconds)
    user_name VARCHAR(50) NOT NULL UNIQUE,
    user_password VARCHAR(50) NOT NULL,
    user_email VARCHAR(50) NOT NULL UNIQUE,
    user_role  VARCHAR(20) NOT NULL
);



CREATE TABLE table_authors (
    author_id BIGINT PRIMARY KEY,  -- will store timestamp (in milliseconds or seconds)
	author_user_id BIGINT NOT NULL,
    author_name VARCHAR(50) , --author actual name
    author_email VARCHAR(50),
    author_subject_a VARCHAR(50),
	author_subject_b VARCHAR(50),
	author_subject_c VARCHAR(50),
	author_subject_d VARCHAR(50),
	
	CONSTRAINT fk_authors_users_user_id
        FOREIGN KEY (author_user_id)
        REFERENCES table_users(user_id)
        ON DELETE SET NULL
);



CREATE TABLE table_participants (
    participant_id BIGINT PRIMARY KEY,  -- will store timestamp (in milliseconds or seconds)
	participant_user_id BIGINT NOT NULL,
    participant_name VARCHAR(50) , --participant actual name
    participant_email VARCHAR(50),
    preferred_subject_a VARCHAR(50),
	preferred_subject_b VARCHAR(50),
	preferred_subject_c VARCHAR(50),
	preferred_subject_d VARCHAR(50),

	CONSTRAINT fk_participants_users_user_id
        FOREIGN KEY (participant_user_id)
        REFERENCES table_users(user_id)
        ON DELETE SET NULL
);

CREATE TABLE table_quizzes (
    quiz_id BIGINT PRIMARY KEY,                 -- Auto-incremented unique quiz ID
    quiz_title VARCHAR(150) NOT NULL,                -- Title of the quiz
    quiz_subject VARCHAR(50) NOT NULL,              -- Subject or category
    quiz_author_id BIGINT NOT NULL,                  -- FK: Refers to users.user_id
    quiz_author_name VARCHAR(50) , 
	quiz_num_questions INT NOT NULL,                 -- Total number of questions
    quiz_marks_per_question FLOAT NOT NULL,          -- Marks per question
    quiz_negative_marks FLOAT DEFAULT 0.0,           -- Negative marks, optional
    quiz_maximum_marks FLOAT DEFAULT 0.0,
	quiz_status INT NOT NULL,            	        -- Quiz status(active,inactive,live)
	created_at TIMESTAMP,
	quiz_time_per_question INTEGER DEFAULT 0,
	quiz_duration INTEGER DEFAULT 0,  -- Duration in minutes
    quiz_start_time TIMESTAMP,
    quiz_end_time TIMESTAMP,
    allow_multiple_attempts BOOLEAN DEFAULT FALSE,
	quiz_difficulty_level VARCHAR(20),
	quiz_instructions TEXT,
	quiz_completions INTEGER DEFAULT 0,
    quiz_average_score DECIMAL(5,2) DEFAULT 0.00,
	quiz_average_time INTEGER,
	quiz_num_allowed_attempt INTEGER,
	
	CONSTRAINT fk_quizzes_users
        FOREIGN KEY (quiz_author_id)
        REFERENCES table_users(user_id)
        ON DELETE SET NULL
    
);


CREATE TABLE table_questions (
    question_id BIGINT PRIMARY KEY,
    question_quiz_id BIGINT NOT NULL ,
	question_author_id BIGINT NOT NULL ,
    question_question_text TEXT,
    question_option_a VARCHAR(100),
    question_option_b VARCHAR(100),
    question_option_c VARCHAR(100),
    question_option_d VARCHAR(100),
	question_mark FLOAT NOT NULL,
	question_negative_mark FLOAT NOT NULL,
	questions_attempted INT, -- number of participants attempted the question
	questions_attempted_correct INT, -- number of participants gave correct anwswer
    question_correct_option VARCHAR(5),
	question_correct_answer VARCHAR(100),
	question_is_saved BOOLEAN,
	created_at TIMESTAMP,

	CONSTRAINT fk_questions_quizzes
        FOREIGN KEY (question_quiz_id)
        REFERENCES table_quizzes(quiz_id)
        ON DELETE SET NULL,

	CONSTRAINT fk_questions_users
        FOREIGN KEY (question_author_id)
        REFERENCES table_users(user_id)
        ON DELETE SET NULL
);

CREATE TABLE table_quiz_attempt (
    attempt_id BIGINT PRIMARY KEY,
    attempt_quiz_id BIGINT REFERENCES table_quizzes(quiz_id),
    attempt_participant_id BIGINT REFERENCES table_participants(participant_id),
    attempt_start_time TIMESTAMP,
    attempt_end_time TIMESTAMP,
	attempt_quiz_time_taken INTEGER,
    attempt_status VARCHAR(20),  -- 'In Progress', 'Completed'
    attempt_score FLOAT,
    attempt_total_marks FLOAT,
    attempt_correct_answers INTEGER,
    attempt_wrong_answers INTEGER,
    attempt_unanswered_questions INTEGER,
	attempt_num INTEGER -- number of attempts made by participant
);

CREATE TABLE table_participant_answer (
    participant_answer_id BIGINT PRIMARY KEY,
    participant_answer_attempt_id BIGINT REFERENCES table_quiz_attempt(attempt_id),
    participant_answer_question_id BIGINT REFERENCES table_questions(question_id),
	participant_answer_selected_answer VARCHAR(100),
    participant_answer_selected_option CHAR(1),  -- 'A', 'B', 'C', 'D'
    participant_answer_timestamp TIMESTAMP,
	participant_answer_correct_answer BOOLEAN
);


--ALTER TABLE table_quizzes
--DROP CONSTRAINT fk_quizzes_users;
--DROP TABLE table_questions CASCADE;
--TRUNCATE TABLE table_questions;
