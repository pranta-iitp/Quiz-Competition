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
    

@author_bp.route('/authors_list', methods=['GET'])
def get_authors():
    """
    Fetch all authors with their basic information
    Returns JSON list of all authors
    """
    try:
        # Query all authors with user information (if needed)
        authors = db.session.query(Authors, Users).join(
            Users, Authors.author_user_id == Users.user_id
        ).all()
        
        # Alternative: Simple query if you don't need user details
        # authors = Authors.query.all()
        
        authors_list = []
        for author, user in authors:
            author_data = {
                'author_id': author.author_id,
                'author_name': author.author_name,
                'author_email': author.author_email,
                'author_subject_a': author.author_subject_a,
                'author_subject_b': author.author_subject_b,
                'author_subject_c': author.author_subject_c,
                'author_subject_d': author.author_subject_d,
                'user_name': user.user_name,  # From Users table
                'user_role': user.user_role   # From Users table
            }
            authors_list.append(author_data)
        print('author_data',author_data)
        return jsonify({
            'success': True,
            'data': authors_list,
            'total': len(authors_list)
        }), 200
        
    except Exception as e:
        #logger.error(f"Error fetching authors: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to fetch authors',
            'error': str(e)
        }), 500


"""
@author_bp.route('/api/authors/<int:author_id>', methods=['GET'])
def get_author_by_id(author_id):
    
    #Fetch a specific author by ID with detailed information
    
    try:
        author_data = db.session.query(Authors, Users).join(
            Users, Authors.author_user_id == Users.user_id
        ).filter(Authors.author_id == author_id).first()
        
        if not author_data:
            return jsonify({
                'success': False,
                'message': 'Author not found'
            }), 404
        
        author, user = author_data
        
        # Get quiz statistics for this author
        quiz_stats = db.session.query(
            func.count(Quizzes.quiz_id).label('total_quizzes'),
            func.avg(Quizzes.quiz_average_score).label('avg_score'),
            func.sum(Quizzes.quiz_completions).label('total_completions')
        ).filter(Quizzes.quiz_author_id == author_id).first()
        
        author_detail = {
            'author_id': author.author_id,
            'author_name': author.author_name,
            'author_email': author.author_email,
            'author_subject_a': author.author_subject_a,
            'author_subject_b': author.author_subject_b,
            'author_subject_c': author.author_subject_c,
            'author_subject_d': author.author_subject_d,
            'user_name': user.user_name,
            'user_role': user.user_role,
            'statistics': {
                'total_quizzes': quiz_stats.total_quizzes or 0,
                'average_score': float(quiz_stats.avg_score or 0),
                'total_completions': quiz_stats.total_completions or 0
            }
        }
        
        return jsonify({
            'success': True,
            'data': author_detail
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching author {author_id}: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to fetch author details',
            'error': str(e)
        }), 500

@author_bp.route('/api/authors/stats', methods=['GET'])
def get_authors_statistics():
    
    #Get overall statistics about authors
    
    try:
        # Total authors
        total_authors = Authors.query.count()
        
        # Active authors (those who created quizzes recently)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        active_authors = db.session.query(Authors).join(
            Quizzes, Authors.author_id == Quizzes.quiz_author_id
        ).filter(Quizzes.created_at >= thirty_days_ago).distinct().count()
        
        # Top subjects
        subject_counts = {}
        authors = Authors.query.all()
        for author in authors:
            subjects = [author.author_subject_a, author.author_subject_b, 
                       author.author_subject_c, author.author_subject_d]
            for subject in subjects:
                if subject and subject.strip():
                    subject_counts[subject] = subject_counts.get(subject, 0) + 1
        
        # Sort subjects by popularity
        top_subjects = sorted(subject_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Recent authors (joined in last 30 days)
        # Assuming you have a created_at field or similar
        # recent_authors = Authors.query.filter(Authors.created_at >= thirty_days_ago).count()
        
        stats = {
            'total_authors': total_authors,
            'active_authors': active_authors,
            'top_subjects': [{'subject': subject, 'count': count} for subject, count in top_subjects],
            # 'recent_authors': recent_authors
        }
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching author statistics: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to fetch statistics',
            'error': str(e)
        }), 500

@author_bp.route('/api/authors/search', methods=['GET'])
def search_authors():
    
    #Search authors by name, email, or subject
    
    try:
        # Get search parameters
        query = request.args.get('q', '').strip()
        subject = request.args.get('subject', '').strip()
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Build the query
        authors_query = db.session.query(Authors, Users).join(
            Users, Authors.author_user_id == Users.user_id
        )
        
        # Apply search filters
        if query:
            search_filter = f"%{query}%"
            authors_query = authors_query.filter(
                db.or_(
                    Authors.author_name.ilike(search_filter),
                    Authors.author_email.ilike(search_filter),
                    Users.user_name.ilike(search_filter)
                )
            )
        
        if subject:
            subject_filter = f"%{subject}%"
            authors_query = authors_query.filter(
                db.or_(
                    Authors.author_subject_a.ilike(subject_filter),
                    Authors.author_subject_b.ilike(subject_filter),
                    Authors.author_subject_c.ilike(subject_filter),
                    Authors.author_subject_d.ilike(subject_filter)
                )
            )
        
        # Get total count for pagination
        total_count = authors_query.count()
        
        # Apply pagination
        authors = authors_query.offset(offset).limit(limit).all()
        
        authors_list = []
        for author, user in authors:
            author_data = {
                'author_id': author.author_id,
                'author_name': author.author_name,
                'author_email': author.author_email,
                'author_subject_a': author.author_subject_a,
                'author_subject_b': author.author_subject_b,
                'author_subject_c': author.author_subject_c,
                'author_subject_d': author.author_subject_d,
                'user_name': user.user_name,
                'user_role': user.user_role
            }
            authors_list.append(author_data)
        
        return jsonify({
            'success': True,
            'data': authors_list,
            'total': total_count,
            'limit': limit,
            'offset': offset,
            'has_more': offset + limit < total_count
        }), 200
        
    except Exception as e:
        logger.error(f"Error searching authors: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to search authors',
            'error': str(e)
        }), 500

@author_bp.route('/api/authors/<int:author_id>/quizzes', methods=['GET'])
def get_author_quizzes(author_id):
    
    #Get all quizzes created by a specific author
    
    try:
        # Verify author exists
        author = Authors.query.get(author_id)
        if not author:
            return jsonify({
                'success': False,
                'message': 'Author not found'
            }), 404
        
        # Get author's quizzes
        quizzes = Quizzes.query.filter_by(quiz_author_id=author_id).order_by(
            desc(Quizzes.created_at)
        ).all()
        
        quizzes_list = []
        for quiz in quizzes:
            quiz_data = {
                'quiz_id': quiz.quiz_id,
                'quiz_title': quiz.quiz_title,
                'quiz_subject': quiz.quiz_subject,
                'quiz_num_questions': quiz.quiz_num_questions,
                'quiz_maximum_marks': float(quiz.quiz_maximum_marks),
                'quiz_duration': quiz.quiz_duration,
                'quiz_status': quiz.quiz_status,
                'quiz_completions': quiz.quiz_completions,
                'quiz_average_score': float(quiz.quiz_average_score or 0),
                'created_at': quiz.created_at.isoformat() if quiz.created_at else None,
                'quiz_difficulty_level': quiz.quiz_difficulty_level
            }
            quizzes_list.append(quiz_data)
        
        return jsonify({
            'success': True,
            'data': {
                'author': {
                    'author_id': author.author_id,
                    'author_name': author.author_name,
                    'author_email': author.author_email
                },
                'quizzes': quizzes_list,
                'total_quizzes': len(quizzes_list)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching quizzes for author {author_id}: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to fetch author quizzes',
            'error': str(e)
        }), 500

# Error handlers
@author_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': 'Resource not found'
    }), 404

@author_bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({
        'success': False,
        'message': 'Internal server error'
    }), 500
"""