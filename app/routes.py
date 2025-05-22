from flask import render_template, request
from app import app, db
from app.models import Users,Authors,Participants,Quizzes
from werkzeug.security import generate_password_hash
from datetime import datetime
import random
from flask import redirect, url_for, flash, session
from werkzeug.security import check_password_hash
import uuid


def generate_user_id():
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')  # 14 digits
    random_part = random.randint(100, 999) # 3 digits
    return f"{timestamp}{random_part}"

@app.route("/")
def home():
    return render_template('index.html')

@app.route('/logout')
def logout_method():
    session.clear()  # Clear all session data
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))  # Redirect to home page

@app.route("/create_quiz")
def create_quiz():
    return render_template('index.html')


"""=====================author code starts==================="""


@app.route('/new_quiz_attr', methods=['GET', 'POST'])
def new_quiz_attr():
    if 'user_id' not in session:
        flash("You must be logged in as author.")
        return redirect(url_for('sign_in'))

    user_id = session['user_id']
    author = Authors.query.filter_by(author_user_id=user_id).first()

    if request.method == 'POST':
        quiz_id = generate_user_id()
        quiz_title = request.form['quiz_title']
        quiz_subject = request.form['quiz_subject']
        quiz_author_id = request.form['quiz_author_id']
        quiz_subject = request.form['quiz_subject']
        quiz_num_questions = request.form['quiz_num_questions']
        quiz_marks_per_question = request.form['quiz_marks_per_question']
        quiz_negative_marks = request.form['quiz_negative_marks']
        # Create quiz 
        quiz = Quizzes(
            quiz_id=quiz_id,
            quiz_title=quiz_title,
            quiz_subject=quiz_subject,
            quiz_author_id = author.author_user_id,
            quiz_num_questions = quiz_num_questions,
            quiz_marks_per_question = quiz_marks_per_question,
            quiz_negative_marks = quiz_negative_marks,
            quiz_is_live = False
        )
        db.session.add(quiz)
        db.session.commit()
        #flash('Profile updated successfully!', 'success')
        return redirect(url_for('author_dashboard'))
    print("author",author)
    return render_template('author_pages/update_author_profile.html', author=author)


@app.route('/update_profile_author', methods=['GET', 'POST'])
def update_profile_author():
    if 'user_id' not in session:
        flash("You must be logged in as author.")
        return redirect(url_for('sign_in'))

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
        return redirect(url_for('author_dashboard'))
    print("author",author)
    return render_template('author_pages/update_author_profile.html', author=author)

# author single page application code
@app.route('/author/section/<string:section_name>')
def load_author_section(section_name):
    if section_name == 'new_quiz':
        user_id = session.get('user_id')
        user = Authors.query.filter_by(author_user_id=user_id).first()
        return render_template('author_pages/new_quiz_attibutes.html', author=user)
    elif section_name == 'all_quizzes':
        return render_template('author_pages/all_quizzes.html')
    elif section_name == 'active_quizzes':
        return render_template('author_pages/active_quizzes.html')
    elif section_name == 'inactive_quizzes':
        return render_template('author_pages/inactive_quizzes.html')
    elif section_name == 'archived_quizzes':
        return render_template('author_pages/archived_quizzes.html')
    elif section_name == 'update_profile_author':
        user_id = session.get('user_id')
        user = Authors.query.filter_by(author_user_id=user_id).first()
        return render_template('author_pages/update_author_profile.html', author=user)
    return "<p>Invalid section</p>"

"""============================author code ends===================="""


""" ====================participant code starts ===================="""
# participant - profile update
@app.route('/update_profile_participant', methods=['GET', 'POST'])
def update_profile_participant():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in", "warning")
        return redirect(url_for('sign_in'))

    # Fetch participant linked to user_id from database
    participant = Participants.query.filter_by(participant_user_id=user_id).first()

    if request.method == 'POST':
        participant.participant_name = request.form['participant_name']
        participant.preferred_subject_a = request.form['preferred_subject_a']
        participant.preferred_subject_b = request.form['preferred_subject_b']
        participant.preferred_subject_c = request.form['preferred_subject_c']
        participant.preferred_subject_d = request.form['preferred_subject_d']
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('participant_dashboard'))

    return render_template("update_profile_participant.html", participant=participant)

# participant single page application code
@app.route('/participant/section/<string:section_name>')
def load_participant_section(section_name):
    if section_name == 'quizzes':
        return render_template('partials/available_quizzes.html')
    elif section_name == 'scores':
        return render_template('partials/my_scores.html')
    elif section_name == 'update_profile':
        user_id = session.get('user_id')
        user = Users.query.filter_by(user_id=user_id).first()
        return render_template('partials/update_profile_form.html', user=user)
    return "<p>Invalid section</p>"
"""===================participant code ends=========="""

# sign-in code
@app.route('/submit_sign_in', methods=['GET', 'POST'])
def submit_sign_in():
    if request.method == 'POST':
        print("Form received:", request.form)
        email = request.form.get('email')
        password = request.form.get('password')
        print("Email:", email, "Password:", password)
        user = Users.query.filter_by(user_email=email).first()
        print(user)
        if user and user.user_password == password:  # use check_password_hash if storing hashed passwords
            session['user_id'] = user.user_id
            session['user_role'] = user.user_role
            session['user_name'] = user.user_name

            # Redirect based on role
            if user.user_role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.user_role == 'superuser':
                return redirect(url_for('superuser_dashboard'))
            elif user.user_role == 'author':
                return redirect(url_for('author_dashboard'))
            elif user.user_role == 'participant':
                return redirect(url_for('participant_dashboard'))
            else:
                flash('Unknown user role.', 'danger')
                return redirect(url_for('sign_in'))
        else:
            flash('Invalid email or password.', 'danger')
            return render_template('sign_in.html')

    return render_template('sign_in.html')


@app.route('/admin/dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/superuser/dashboard')
def superuser_dashboard():
    return render_template('superuser_dashboard.html')

@app.route('/author/dashboard')
def author_dashboard():
    return render_template('author_dashboard.html')

@app.route('/participant/dashboard')
def participant_dashboard():
    return render_template('participant_dashboard.html')



@app.route('/sign_in',methods=['GET', 'POST'])
def sign_in():
    return render_template('sign_in.html')

@app.route('/register_author', methods=['GET', 'POST'])
def register_author():
    if request.method == 'POST':
        print("dad1")
        user_id = generate_user_id()
        
        # form data
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # For the time being we are using the password that is set by the user
        hashed_password = password  

        # Create User and 
        user = Users(
            user_id=user_id,
            user_name=username,
            user_email=email,
            user_password=hashed_password,
            user_role="author"
        )
        db.session.add(user)
        db.session.commit()
        author_id = generate_user_id()  
        # Create Author
        author = Authors(
            author_id=author_id,
            author_user_id=user_id,
            author_name=None,
            author_email=email,
            author_subject_a=None,
            author_subject_b=None,
            author_subject_c=None,
            author_subject_d=None
        )

        db.session.add(author)
        db.session.commit()

        return render_template('register_success.html')
    return render_template('register_author.html')

@app.route('/register_participant', methods=['GET', 'POST'])
def register_participant():
    if request.method == 'POST':
        print("dad")
        user_id = generate_user_id()
        # form data
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = password
        user = Users(user_id=user_id,user_name=username, user_email=email, user_password=hashed_password,user_role="participant")
        db.session.add(user)
        db.session.commit()
        print(user)
        participant_id = generate_user_id()  
        # Create participant
        participant = Participants(
            participant_id=participant_id,
            participant_user_id=user_id,
            participant_name=None,
            participant_email=email,
            preferred_subject_a=None,
            preferred_subject_b=None,
            preferred_subject_c=None,
            preferred_subject_d=None
        )

        db.session.add(participant)
        db.session.commit()

        return render_template('register_success.html')
    return render_template('register_participant.html')
