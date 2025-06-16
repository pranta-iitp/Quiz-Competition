# app/routes/author.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session,jsonify
from app import db
from app.models import Users, Authors, Quizzes, Questions
from app.util import generate_user_id
from sqlalchemy import cast, Integer,text
from sqlalchemy.exc import SQLAlchemyError
from app.encryption_utils import encrypt_user_id, decrypt_user_id, encrypt_multiple_values, decrypt_multiple_values


author_bp = Blueprint('author', __name__)


@author_bp.route('/dashboard')
def dashboard():
    user_id = session['user_id']
    user_role = session['user_role']
    user_name = session['user_name']

    if not user_id or not user_role or not user_name:
        flash('Missing user data in URL parameters.', 'danger')
        return redirect(url_for('auth.sign_in'))

    author = Authors.query.filter_by(author_user_id=user_id).first()
    quizzes = Quizzes.query.filter_by(quiz_author_id=user_id).all()

    return render_template(
        'author/author_dashboard.html',
        author=author,
        quizzes=quizzes
    )

# active and live
@author_bp.route('/active_quizzes', methods=['GET', 'POST'])
def active_quizzes():
    if 'user_id' not in session:
        flash("You must be logged in to view quizzes.")
        return redirect(url_for('auth.sign_in'))
    
    author = Authors.query.filter_by(author_user_id=session['user_id']).first()
    quizzes = Quizzes.query.filter(
        Quizzes.quiz_author_id == author.author_user_id,
        cast(Quizzes.quiz_status, Integer) == 1
    ).all()
    return render_template('author/active_quizzes.html', quizzes=quizzes, author=author)

# inactive
@author_bp.route('/inactive_quizzes', methods=['GET', 'POST'])
def inactive_quizzes():
    if 'user_id' not in session:
        flash("You must be logged in to view quizzes.")
        return redirect(url_for('auth.sign_in'))
    
    author = Authors.query.filter_by(author_user_id=session['user_id']).first()
    quizzes = Quizzes.query.filter(
        Quizzes.quiz_author_id == author.author_user_id,
        Quizzes.quiz_status == 2
    ).all()
    return render_template('author/inactive_quizzes.html', quizzes=quizzes)

@author_bp.route('/all_quizzes', methods=['GET', 'POST'])
def all_quizzes():
    if 'user_id' not in session:
        flash("You must be logged in to view quizzes.")
        return redirect(url_for('auth.sign_in'))
    
    author = Authors.query.filter_by(author_user_id=session['user_id']).first()
    print("all******",author)
    if not author:
        flash("Author profile not found.")
        return redirect(url_for('author.dashboard'))

    quizzes = Quizzes.query.filter_by(quiz_author_id=author.author_user_id).all()
    return render_template('author/all_quizzes.html', quizzes=quizzes,author=author)

@author_bp.route('/new_quiz_attr', methods=['GET', 'POST'])
def new_quiz_attr():
    if 'user_id' not in session:
        print("entry_authoradasd")
        flash("You must be logged in as author.")
        return redirect(url_for('auth.sign_in'))

    user_id = session['user_id']
    author = Authors.query.filter_by(author_user_id=user_id).first()
    messages = {'error': None, 'success': None}
    if request.method == 'POST':
        try:
            print("auth0011")
            quiz_title = request.form['quiz_title']
            quiz_subject = request.form['quiz_subject']
            sql = text("SELECT * FROM table_quizzes WHERE quiz_title = :title AND quiz_subject = :subject AND quiz_author_id = :user_id")
            result = db.session.execute(sql, {'title': quiz_title,'subject':quiz_subject,'user_id':user_id}).fetchone()
            # Develop a functionality - when 'result' is None then error message will be passed to author_dashboard.html
            if result is not None:
                flash(f"A quiz with the title '{quiz_title}' already exists under subject '{quiz_subject}'. Please choose a different title.", "error")
                return redirect(url_for('author.new_quiz_attr'))
            quiz_id = generate_user_id()
            quiz_num_questions = request.form['quiz_num_questions']
            quiz_marks_per_question = request.form['quiz_marks_per_question']
            quiz_negative_marks = request.form['quiz_negative_marks']
            quiz_time_per_question = request.form['quiz_time_per_question']
            quiz_duration = int(quiz_time_per_question) * int(quiz_num_questions)
            quiz_num_allowed_attempt = int(request.form['quiz_num_allowed_attempt'])
            quiz_maximum_marks = int(quiz_num_questions) * float(quiz_marks_per_question)
            # Create new quiz
            quiz = Quizzes(
                quiz_id=quiz_id,
                quiz_title=quiz_title,
                quiz_subject=quiz_subject,
                quiz_author_id=author.author_user_id,
                quiz_num_questions=quiz_num_questions,
                quiz_marks_per_question=quiz_marks_per_question,
                quiz_negative_marks=quiz_negative_marks,
                quiz_maximum_marks=quiz_maximum_marks,
                quiz_status=2, # 2 =inactive
                created_at=None,
                quiz_time_per_question = quiz_time_per_question,
                quiz_duration = quiz_duration,
                quiz_num_allowed_attempt = quiz_num_allowed_attempt
            )
            db.session.add(quiz)
            db.session.commit()
            # Create questions
            for _ in range(1,int(quiz_num_questions)+1):
                question_id = generate_user_id()
                new_question = Questions(
                    question_id=question_id,
                    question_quiz_id=quiz_id,
                    question_author_id=user_id,
                    question_question_text=None,
                    question_option_a=None,
                    question_option_b=None,
                    question_option_c=None,
                    question_option_d=None,
                    question_correct_option=None,
                    question_mark=float(quiz_marks_per_question),
                    question_negative_mark=float(quiz_negative_marks),
                    questions_attempted=0,
                    questions_attempted_correct=0,
                    question_is_saved = False
                )
                db.session.add(new_question)

                db.session.commit()
            flash("Quiz created successfully!", "success")
            return redirect(url_for('author.dashboard'))

        except SQLAlchemyError as e:
            db.session.rollback()
            flash("An error occurred while creating the quiz. Please try again.", "error")
            print(f"Database error: {e}")
            return redirect(url_for('author.new_quiz_attr'))

        except Exception as e:
            db.session.rollback()
            flash("Unexpected error. Please contact support.", "error")
            print(f"Unexpected error: {e}")
            return redirect(url_for('author.new_quiz_attr'))

    # For GET request
    return render_template('author/author_dashboard.html', author=author, messages=messages)


@author_bp.route('/update_author_profile', methods=['GET', 'POST'])
def update_author_profile():
    if 'user_id' not in session:
        flash("You must be logged in as author.")
        return redirect(url_for('auth.sign_in'))
    print("update author")
    user_id = session['user_id']
    author = Authors.query.filter_by(author_user_id=user_id).first()

    if request.method == 'POST':
        # Update fields (email is not editable)
        author.author_name = request.form['author_name']
        author.author_subject_a = request.form['author_subject_a']
        author.author_subject_b = request.form['author_subject_b']
        author.author_subject_c = request.form['author_subject_c']
        author.author_subject_d = request.form['author_subject_d']
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('author.dashboard'))
    print("author",author)
    return render_template('author/update_author_profile.html', author=author)

# author single page application code
@author_bp.route('/section/<author_user_id>/<string:section_name>')
def load_author_section(author_user_id,section_name):
    if section_name == 'new_quiz':
        user_id = session.get('user_id')
        user = Authors.query.filter_by(author_user_id=user_id).first()
        return render_template('author/new_quiz_attr.html', author=user)
    elif section_name == 'all_quizzes':
        author = Authors.query.filter_by(author_user_id=author_user_id).first()
        quizzes = Quizzes.query.filter_by(quiz_author_id=author_user_id).all()
        # make changes here all_quizzes1.html to all_quizzes.html
        return render_template('author/all_quizzes.html',author=author,quizzes=quizzes)
    elif section_name == 'manage_quizzes':
        author = Authors.query.filter_by(author_user_id=author_user_id).first()
        quizzes = Quizzes.query.filter_by(quiz_author_id=author_user_id).all()
        return render_template('author/manage_quizzes.html',author=author,quizzes=quizzes)
    elif section_name == 'update_profile_author':
        user_id = session.get('user_id')
        print("ad")
        author = Authors.query.filter_by(author_user_id=user_id).first()
        return render_template('author/update_author_profile.html', author=author)
    elif section_name == 'active_quizzes':
        user_id = session.get('user_id')
        author = Authors.query.filter_by(author_user_id=user_id).first()
        quizzes = Quizzes.query.filter_by(quiz_author_id=author.author_user_id).all()
        return render_template('author/active_quizzes.html',author=author,quizzes=quizzes)
    elif section_name == 'inactive_quizzes':
        user_id = session.get('user_id')
        author = Authors.query.filter_by(author_user_id=user_id).first()
        quizzes = Quizzes.query.filter_by(quiz_author_id=author.author_user_id).all()
        return render_template('author/inactive_quizzes.html',author=author,quizzes=quizzes)
    elif section_name == 'archived_quizzes':
        return render_template('author/archived_quizzes.html')
    
    return "<p>Invalid section</p>"

# quiz tab single page application code
@author_bp.route('/get_quiz/<quiz_author_id>/<string:section_name>')
def get_quiz(quiz_author_id,section_name):
    try:
        print('section_name',section_name,section_name.lower())
        quizStatus = 0
        if(section_name.lower() == 'active'):
            quizStatus = 1
        elif(section_name.lower() == 'inactive'):
            quizStatus = 2
        elif(section_name.lower() == 'archived'):
            quizStatus = 3

        #print('attempt_id entry',attempt_id)
        quizzes = Quizzes.query.filter_by(quiz_author_id=quiz_author_id, quiz_status = quizStatus).all()
        
        # Check if attempt exists
        if not quizzes:
            return jsonify({
                'success': False,
                'error': 'Attempt not found'
            }), 404
        
        all_quiz_data = []
        for individual_quiz in quizzes:
            all_quiz_data.append({
                'quiz_id': str(individual_quiz.quiz_id),
                'quiz_title': str(individual_quiz.quiz_title),
                'question_count':individual_quiz.quiz_num_questions,
                'quiz_mark_per_question':individual_quiz.quiz_marks_per_question,
                'quiz_negative_mark_per_question':individual_quiz.quiz_negative_marks,
                'quiz_maximum_marks':individual_quiz.quiz_maximum_marks
            })
        print(all_quiz_data)
        return jsonify({
            'success': True,
            'allQuizData': all_quiz_data
        })
    except Exception as e:
        print(f"Error in get_attempt_stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500