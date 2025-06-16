-- Drop child tables first to avoid foreign key constraint errors
DROP TABLE IF EXISTS table_participant_answer CASCADE;
DROP TABLE IF EXISTS table_quiz_attempt CASCADE;
DROP TABLE IF EXISTS table_questions CASCADE;
DROP TABLE IF EXISTS table_quizzes CASCADE;
DROP TABLE IF EXISTS table_participants CASCADE;
DROP TABLE IF EXISTS table_authors CASCADE;
DROP TABLE IF EXISTS table_users CASCADE;
DROP TABLE IF EXISTS table_quiz_status CASCADE;
DROP TABLE IF EXISTS table_roles CASCADE;

-- Drop the ENUM type after all tables using it are dropped
--DROP TYPE IF EXISTS user_predefined_role;