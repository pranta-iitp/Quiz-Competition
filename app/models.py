"""It is called a model in Flask-SQLAlchemy and SQLAlchemy terminology. A
 model is a Python class that represents a database table, where each attribute of the class corresponds 
 to a column in the table. In Flask applications, these models are typically subclasses of db.Model (from Flask-SQLAlchemy)
 or a declarative base class, and they are used to interact with the database in an object-oriented way."""

from app import db

class Users(db.Model):
    __tablename__ = 'table_users'
    user_id = db.Column(db.BigInteger, primary_key=True)
    user_name = db.Column(db.String(50), unique=True, nullable=False)
    user_password = db.Column(db.String(50), nullable=False)
    user_email = db.Column(db.String(50), unique=True, nullable=False)
    user_role = db.Column(db.String(20),nullable=False)

class Authors(db.Model):
    __tablename__ = 'table_authors'
    author_id = db.Column(db.BigInteger, primary_key=True)
    author_user_id = db.Column(db.BigInteger, db.ForeignKey('table_users.user_id'), nullable=False)
    author_name =  db.Column(db.String(50),nullable=True)
    author_email =  db.Column(db.String(50))
    author_subject_a =  db.Column(db.String(50),nullable=True)
    author_subject_b =  db.Column(db.String(50),nullable=True)
    author_subject_c =  db.Column(db.String(50),nullable=True)
    author_subject_d =  db.Column(db.String(50),nullable=True)

class Participants(db.Model):
    __tablename__ = 'table_participants'
    participant_id = db.Column(db.BigInteger, primary_key=True)
    participant_user_id = db.Column(db.BigInteger, db.ForeignKey('table_users.user_id'), nullable=False)
    participant_name =  db.Column(db.String(50),nullable=True)
    participant_email =  db.Column(db.String(50))
    preferred_subject_a =  db.Column(db.String(50),nullable=True)
    preferred_subject_b =  db.Column(db.String(50),nullable=True)
    preferred_subject_c =  db.Column(db.String(50),nullable=True)
    preferred_subject_d =  db.Column(db.String(50),nullable=True)

class Quizzes(db.Model):
    __tablename__ = 'table_quizzes'
    quiz_id = db.Column(db.BigInteger, primary_key=True)
    quiz_title = db.Column(db.String(150),nullable=False)
    quiz_subject =  db.Column(db.String(50),nullable=False)
    quiz_author_id =  db.Column(db.BigInteger, nullable=False)
    quiz_author_name = db.Column(db.String(50),nullable=True)
    quiz_num_questions =  db.Column(db.Integer)
    quiz_marks_per_question =  db.Column(db.Float, nullable=False, default=0.0)
    quiz_negative_marks =  db.Column(db.Float, nullable=False, default=0.0)
    quiz_maximum_marks =  db.Column(db.Float, nullable=False, default=0.0)
    quiz_status =  db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    quiz_duration = db.Column(db.Integer, default=0)  # Duration in seconds
    quiz_time_per_question = db.Column(db.Integer, default=0)
    quiz_start_time = db.Column(db.DateTime)
    quiz_end_time = db.Column(db.DateTime)
    allow_multiple_attempts = db.Column(db.Boolean, default=False)
    # added later
    quiz_difficulty_level = db.Column(db.String(20))
    quiz_instructions = db.Column(db.Text)
    quiz_completions = db.Column(db.Integer, default=0)
    quiz_average_score = db.Column(db.Numeric(5, 2), default=0.00)
    quiz_average_time = db.Column(db.Integer)
    quiz_num_allowed_attempt = db.Column(db.Integer)

class Questions(db.Model):
    __tablename__ = 'table_questions'
    question_id = db.Column(db.BigInteger, primary_key=True)
    question_quiz_id = db.Column(db.BigInteger, db.ForeignKey('table_quizzes.quiz_id'), nullable=False)
    question_author_id = db.Column(db.BigInteger, db.ForeignKey('table_users.user_id'), nullable=False)
    question_question_text = db.Column(db.Text)
    question_option_a = db.Column(db.String(100),nullable=False)
    question_option_b = db.Column(db.String(100),nullable=False)
    question_option_c = db.Column(db.String(100),nullable=False)
    question_option_d = db.Column(db.String(100),nullable=False)
    question_correct_option = db.Column(db.String(5),nullable=True)
    question_correct_answer = db.Column(db.String(100),nullable=False)
    question_mark = db.Column(db.Float)
    question_negative_mark = db.Column(db.Float)
    questions_attempted = db.Column(db.Integer)
    questions_attempted_correct = db.Column(db.Integer)
    question_is_saved = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime)


# Quiz Attempt Model
class QuizAttempt(db.Model):
    __tablename__ = 'table_quiz_attempt'
    attempt_id = db.Column(db.BigInteger, primary_key=True)
    attempt_quiz_id = db.Column(db.BigInteger, db.ForeignKey('table_quizzes.quiz_id'))
    attempt_participant_id = db.Column(db.BigInteger, db.ForeignKey('table_participants.participant_id'))
    attempt_start_time = db.Column(db.DateTime)
    attempt_end_time = db.Column(db.DateTime)
    attempt_quiz_time_taken = db.Column(db.Integer)
    attempt_status = db.Column(db.String(20))  # 'In Progress', 'Completed'
    attempt_score =  db.Column(db.Float)
    attempt_total_marks =  db.Column(db.Float)
    attempt_correct_answers = db.Column(db.Integer)
    attempt_wrong_answers = db.Column(db.Integer)
    attempt_unanswered_questions = db.Column(db.Integer)
    attempt_num = db.Column(db.Integer)

# Participant Answer Model
class ParticipantAnswer(db.Model):
    __tablename__ = 'table_participant_answer'
    participant_answer_id =db.Column(db.BigInteger, primary_key=True)
    participant_answer_attempt_id = db.Column(db.BigInteger, db.ForeignKey('table_quiz_attempt.attempt_id'))
    participant_answer_question_id = db.Column(db.BigInteger, db.ForeignKey('table_questions.question_id'))
    participant_answer_selected_answer = db.Column(db.String(100),nullable=False)
    participant_answer_selected_option = db.Column(db.String(1))  # 'A', 'B', 'C', 'D'
    participant_answer_timestamp = db.Column(db.DateTime)
    participant_answer_correct_answer = db.Column(db.Boolean)