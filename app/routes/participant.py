# app/routes/participant.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models import Users, Participants,Quizzes
from sqlalchemy import or_

participant_bp = Blueprint('participant', __name__)

@participant_bp.route('/dashboard')
def dashboard():
    user_id = session['user_id']
    user_role = session['user_role']
    user_name = session['user_name']

    if not user_id or not user_role or not user_name:
        flash('Missing user data in URL parameters.', 'danger')
        return redirect(url_for('auth.sign_in'))

    participant = Participants.query.filter_by(participant_user_id=user_id).first()
    # Initialize an empty list to store preferred subjects
    preferred_subjects = []
    
    # Check if the participant exists
    if participant:
        # Append preferred subjects to the list if they are not None
        if participant.preferred_subject_a:
            preferred_subjects.append(participant.preferred_subject_a)
        if participant.preferred_subject_b:
            preferred_subjects.append(participant.preferred_subject_b)
        if participant.preferred_subject_c:
            preferred_subjects.append(participant.preferred_subject_c)
        if participant.preferred_subject_d:
            preferred_subjects.append(participant.preferred_subject_d)
    quizzes = Quizzes.query.filter(Quizzes.quiz_subject.in_(preferred_subjects)).all()
    return render_template('participant_pages/participant_dashboard.html',participant=participant,
        quizzes=quizzes)

# participant - profile update
@participant_bp.route('/update_profile_participant/<participant_id>', methods=['GET', 'POST'])
def update_profile_participant(participant_id):
    # Fetch participant linked to user_id from database
    participant = Participants.query.filter_by(participant_id=participant_id).first()
    print("update participant")
    if request.method == 'POST':
        participant.participant_name = request.form['participant_name']
        participant.preferred_subject_a = request.form['preferred_subject_a']
        participant.preferred_subject_b = request.form['preferred_subject_b']
        participant.preferred_subject_c = request.form['preferred_subject_c']
        participant.preferred_subject_d = request.form['preferred_subject_d']
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('participant.dashboard'))

    return render_template("participant_pages/update_profile_form.html", participant=participant)

# participant single page application code
@participant_bp.route('/section/<participant_id>/<section_name>', methods=['GET', 'POST'])
def load_participant_section(participant_id,section_name):
    #print('section_name',section_name)
    if section_name == 'available_quizzes':
        if request.is_json:
            data = request.get_json()
            sub_a = data.get('preferred_subject_a').strip()
            sub_b = data.get('preferred_subject_b').strip()
            sub_c = data.get('preferred_subject_c').strip()
            sub_d = data.get('preferred_subject_d').strip()
            subjects_to_check = []
            if(len(sub_a) > 0):
                subjects_to_check.append(sub_a)
            if(len(sub_b) > 0):
                subjects_to_check.append(sub_b)
            if(len(sub_c) > 0):
                subjects_to_check.append(sub_c)
            if(len(sub_d) > 0):
                subjects_to_check.append(sub_d)
    
        # Fetch all quizzes by any author with status == 1(active) and subject in preferred list
        quizzes = Quizzes.query.filter(
            Quizzes.quiz_subject.in_(subjects_to_check),
            Quizzes.quiz_status == 1
        ).all()
        #print('quizzes',quizzes)
        participant = Participants.query.filter_by(participant_id=participant_id).first()
        #print('participant ',participant)
        return render_template('participant_pages/available_quizzes.html',participant=participant,quizzes=quizzes)
    elif section_name == 'scores':
        return render_template('participant_pages/my_scores.html')
    elif section_name == 'update_profile_participant':
        #user_id = session.get('user_id')
        print("participant_id",participant_id)
        participant = Participants.query.filter_by(participant_id=participant_id).first()
        return render_template('participant_pages/update_profile_form.html', participant=participant)
    return "<p>Invalid section</p>"