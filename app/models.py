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
    user_email = db.Column(db.String(50))
    user_role = db.Column(db.String(20),nullable=False)

class Authors(db.Model):
    __tablename__ = 'table_authors'
    author_id = db.Column(db.BigInteger, primary_key=True)
    author_user_id = db.Column(db.BigInteger)
    author_name =  db.Column(db.String(50),nullable=True)
    author_email =  db.Column(db.String(50))
    author_subject_a =  db.Column(db.String(50),nullable=True)
    author_subject_b =  db.Column(db.String(50),nullable=True)
    author_subject_c =  db.Column(db.String(50),nullable=True)
    author_subject_d =  db.Column(db.String(50),nullable=True)

class Participants(db.Model):
    __tablename__ = 'table_participants'
    participant_id = db.Column(db.BigInteger, primary_key=True)
    participant_user_id = db.Column(db.BigInteger)
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
    quiz_num_questions =  db.Column(db.Integer)
    quiz_marks_per_question =  db.Column(db.Float, nullable=False, default=0.0)
    quiz_negative_marks =  db.Column(db.Float, nullable=False, default=0.0)
    quiz_status =  db.Column(db.Integer)
    created_at = db.Column(db.DateTime)

class Questions(db.Model):
    __tablename__ = 'table_questions'
    question_id = db.Column(db.BigInteger, primary_key=True)
    question_quiz_id = db.Column(db.BigInteger) # refering to table_quizzes
    question_author_id = db.Column(db.BigInteger) # refering to table_users
    question_question_text = db.Column(db.Text)
    question_option_a = db.Column(db.String(100),nullable=False)
    question_option_b = db.Column(db.String(100),nullable=False)
    question_option_c = db.Column(db.String(100),nullable=False)
    question_option_d = db.Column(db.String(100),nullable=False)
    question_correct_option = db.Column(db.String(5),nullable=True)
    question_mark = db.Column(db.Float)
    question_negative_mark = db.Column(db.Float)
    questions_attempted = db.Column(db.Integer)
    questions_attempted_correct = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
