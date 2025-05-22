from app import db

class Users(db.Model):
    user_id = db.Column(db.BigInteger, primary_key=True)
    user_name = db.Column(db.String(50), unique=True, nullable=False)
    user_password = db.Column(db.String(50), nullable=False)
    user_email = db.Column(db.String(50))
    user_role = db.Column(db.String(20),nullable=False)

class Authors(db.Model):
    author_id = db.Column(db.BigInteger, primary_key=True)
    author_user_id = db.Column(db.BigInteger)
    author_name =  db.Column(db.String(50),nullable=True)
    author_email =  db.Column(db.String(50))
    author_subject_a =  db.Column(db.String(50),nullable=True)
    author_subject_b =  db.Column(db.String(50),nullable=True)
    author_subject_c =  db.Column(db.String(50),nullable=True)
    author_subject_d =  db.Column(db.String(50),nullable=True)

class Participants(db.Model):
    participant_id = db.Column(db.BigInteger, primary_key=True)
    participant_user_id = db.Column(db.BigInteger)
    participant_name =  db.Column(db.String(50),nullable=True)
    participant_email =  db.Column(db.String(50))
    preferred_subject_a =  db.Column(db.String(50),nullable=True)
    preferred_subject_b =  db.Column(db.String(50),nullable=True)
    preferred_subject_c =  db.Column(db.String(50),nullable=True)
    preferred_subject_d =  db.Column(db.String(50),nullable=True)

class Quizzes(db.Model):
    quiz_id = db.Column(db.BigInteger, primary_key=True)
    quiz_title = db.Column(db.String(150),nullable=False)
    quiz_subject =  db.Column(db.String(50),nullable=False)
    quiz_author_id =  db.Column(db.BigInteger, nullable=False)
    quiz_num_questions =  db.Column(db.BigInteger)
    quiz_marks_per_question =  db.Column(db.Float, nullable=False, default=0.0)
    quiz_negative_marks =  db.Column(db.Float, nullable=False, default=0.0)
    quiz_is_live =  db.Column(db.Boolean, nullable=False, default=False)

