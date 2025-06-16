# app/routes/quiz.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session,jsonify
from app import db
from app.models import Quizzes, Authors,Questions,Participants,QuizAttempt,ParticipantAnswer
from datetime import datetime
from app.util import generate_user_id
from dateutil.parser import parse  
quiz_bp = Blueprint('quiz', __name__)
#current use quiz
@quiz_bp.route('/update_quiz_status/<quiz_id>/<author_id>', methods=['POST'])
def update_quiz_status(quiz_id, author_id):
    if 'user_id' not in session:
        flash("You must be logged in.")
        return redirect(url_for('auth.sign_in'))

    quiz = Quizzes.query.filter_by(quiz_id=quiz_id).first()
    if not quiz:
        flash("Quiz not found.")
        return redirect(url_for('author.all_quizzes'))

    # Check if all questions are completed
    incomplete_questions = Questions.query.filter_by(
        question_quiz_id=quiz_id
    ).filter(
        (Questions.question_question_text == None) | 
        (Questions.question_question_text == '') |
        (Questions.question_is_saved == False)
    ).count()

    if incomplete_questions > 0:
        pass
    new_status = request.form.get('quiz_status')
    new_status = new_status.lower()
    int_new_status = 0
    if(new_status == 'active'):
        int_new_status = 1
    elif(new_status == 'inactive'):
        int_new_status = 2
    elif(new_status == 'archived'):
        int_new_status = 3
    
    if int_new_status == 1 and incomplete_questions> 0:  # Example condition
        flash(f"You cannot activate the quiz titled {quiz.quiz_title} until all the questions of the quiz are done.", "error")
        return redirect(url_for('author.dashboard'))

    status_dict = {'1':'Active','2':'Inactive','3':'Archived'}

    if int_new_status in [1,2,3]:
        quiz.quiz_status = int_new_status
        db.session.commit()
        flash(f"Quiz status updated to {status_dict[str(int_new_status)]}.", "success")
    else:
        flash("Invalid status value.", "error")
    
    return redirect(url_for('author.dashboard'))


@quiz_bp.route('/create_questions/<quiz_id>/<user_id>')
def create_questions(quiz_id,user_id):

    author = Authors.query.filter_by(author_user_id=user_id).first()
    
    # Get the quiz details
    quiz = Quizzes.query.filter_by(quiz_id=quiz_id, quiz_author_id=user_id).first()
    if not quiz:
        flash("Quiz not found or you don't have permission to edit it.", "error")
        return redirect(url_for('author.dashboard'))
    
    # Get existing questions for this quiz
    questions = Questions.query.filter_by(question_quiz_id=quiz_id).order_by(Questions.question_id).all()
    
    return render_template('author/create_questions1.html', quiz=quiz, questions=questions, author=author)


@quiz_bp.route('/view_questions/<quiz_id>/<user_id>')
def view_questions(quiz_id,user_id):

    author = Authors.query.filter_by(author_user_id=user_id).first()
    
    # Get the quiz details
    quiz = Quizzes.query.filter_by(quiz_id=quiz_id, quiz_author_id=user_id).first()
    if not quiz:
        flash("Quiz not found or you don't have permission to edit it.", "error")
        return redirect(url_for('author.dashboard'))
    
    # Get existing questions for this quiz
    questions = Questions.query.filter_by(question_quiz_id=quiz_id).order_by(Questions.question_id).all()
    
    return render_template('author/view_questions.html', quiz=quiz, questions=questions, author=author)


@quiz_bp.route('/save_question/<quiz_id>/<question_id>/<author_id>', methods=['POST'])
def save_question(quiz_id,question_id,author_id):
    print('enrty save_question')
    # Verify quiz ownership
    quiz = Quizzes.query.filter_by(quiz_id=quiz_id, quiz_author_id=author_id).first()
    if not quiz:
        flash("Quiz not found or you don't have permission to edit it.", "error")
        return redirect(url_for('author.dashboard'))
    
    question = Questions.query.filter_by(
            question_id=question_id, 
            question_quiz_id=quiz_id,
            question_author_id = author_id
        ).first()
    try:
        #question_id = request.form['question_id']
        question_text = request.form['question_text']
        option_a = request.form['option_a']
        option_b = request.form['option_b']
        option_c = request.form['option_c']
        option_d = request.form['option_d']
        correct_option = request.form['correct_option']
        question_correct_answer = ''
        
        if(correct_option == 'a' or correct_option == 'A'):
            question_correct_answer = option_a
        elif(correct_option == 'b' or correct_option == 'B'):
            question_correct_answer = option_b
        elif(correct_option == 'c' or correct_option == 'C'):
            question_correct_answer = option_c
        elif(correct_option == 'd' or correct_option == 'D'):
            question_correct_answer = option_d
        #print('question_correct_answer',question_correct_answer)
        if question:
            question.question_question_text = question_text.strip()
            question.question_option_a = option_a.strip()
            question.question_option_b = option_b.strip()
            question.question_option_c = option_c.strip()
            question.question_option_d = option_d.strip()
            question.question_correct_option = str(correct_option)
            question.question_correct_answer = question_correct_answer.strip()
            question.question_is_saved = True
            db.session.commit()
            flash(f"Question saved successfully!", "success")
        else:
            flash("Question not found.", "error")
            
    except Exception as e:
        db.session.rollback()
        flash("Error saving question. Please try again.", "error")
        print(f"Error saving question: {e}")

        print("hello")
        return jsonify({
            'success': False,
            'message': 'Error saving question. Please try again.'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error saving question. Please try again.'
        }), 500
    print('exit save_question')
    return redirect(url_for('quiz.create_questions', quiz_id=quiz_id,user_id=author_id))

@quiz_bp.route('/publish_quiz', methods=['POST'])
def publish_quiz():
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
            quiz_id = data.get('quiz_id')
            author_id = data.get('author_id')
        else:
            quiz_id = request.form.get('quiz_id')
            author_id = request.form.get('author_id')
            
        if not quiz_id or not author_id:
            error_message = 'Missing quiz_id or author_id'
            if request.is_json:
                return jsonify({
                    'success': False, 
                    'message': error_message
                }), 400
            else:
                author = Authors.query.filter_by(author_user_id=author_id).first() if author_id else None
                return render_template('author/author_dashboard.html', 
                                     author=author, 
                                     error_message=error_message)
   
        # Find the quiz and author
        quiz = Quizzes.query.filter_by(quiz_id=quiz_id, quiz_author_id=author_id).first()
        author = Authors.query.filter_by(author_user_id=author_id).first()
        questions = Questions.query.filter_by(question_quiz_id = quiz_id).all()
        if not quiz:
            error_message = "Quiz not found or you don't have permission to publish it."
            if request.is_json:
                return jsonify({
                    'success': False, 
                    'message': error_message
                }), 404
            else:
                return render_template('author/author_dashboard.html', 
                                     author=author, 
                                     error_message=error_message)
        
        # Check if all questions are completed
        incomplete_questions = Questions.query.filter_by(
            question_quiz_id=quiz_id
        ).filter(
            (Questions.question_question_text == None) | 
            (Questions.question_question_text == '') |
            (Questions.question_is_saved == False)
        ).count()
        
        if incomplete_questions > 0:
            error_message = f"Cannot publish quiz. {incomplete_questions} questions are still incomplete."
            if request.is_json:
                return jsonify({
                    'success': False, 
                    'message': error_message
                }), 400
            else:
                 return render_template('quiz/create_questions.html', 
                             quiz=quiz,
                             author=author,
                             questions=questions,
                             error_message=error_message)
        
        # Update quiz status to inactive (2 = inactive, ready for manual activation)
        quiz.quiz_status = 2
        db.session.commit()
        
        success_message = "Quiz published successfully! Status is set to inactive - you can activate it from the dashboard."
        
        if request.is_json:
            return jsonify({
                'success': True,
                'message': success_message
            }), 200
        else:
            return render_template('author/author_dashboard.html', 
                                 author=author, 
                                 success_message=success_message)
        
    except Exception as e:
        db.session.rollback()
        error_message = "Error publishing quiz."
        print(f"Error publishing quiz: {e}")
        
        # Try to get author for template rendering
        try:
            author = Authors.query.filter_by(author_user_id=author_id).first() if 'author_id' in locals() else None
        except:
            author = None
        
        if request.is_json:
            return jsonify({
                'success': False,
                'message': error_message
            }), 500
        else:
            return render_template('author/author_dashboard.html', 
                                 author=author, 
                                 error_message=error_message)
    
# Optional: Delete quiz functionality
@quiz_bp.route('/delete_quiz/<quiz_id>')
def delete_quiz(quiz_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.sign_in'))
    
    user_id = session['user_id']
    
    try:
        quiz = Quizzes.query.filter_by(quiz_id=quiz_id, quiz_author_id=user_id).first()
        if not quiz:
            flash("Quiz not found or you don't have permission to delete it.", "error")
            return redirect(url_for('author.dashboard'))
        
        # Delete associated questions first
        Questions.query.filter_by(question_quiz_id=quiz_id).delete()
        
        # Delete the quiz
        db.session.delete(quiz)
        db.session.commit()
        
        flash(f"Quiz '{quiz.quiz_title}' has been deleted successfully.", "success")
        
    except Exception as e:
        db.session.rollback()
        flash("Error deleting quiz.", "error")
        print(f"Error deleting quiz: {e}")
    
    return redirect(url_for('author.dashboard'))

# participitant attempt quiz function
@quiz_bp.route('/attempt_quiz/<quiz_id>/<participant_id>')
def attempt_quiz(quiz_id,participant_id):
    quiz = Quizzes.query.filter_by(quiz_id=quiz_id).first()
    participant = Participants.query.filter_by(participant_id=participant_id).first()
    questions = Questions.query.filter_by(question_quiz_id=quiz_id).order_by(Questions.question_id).all()
    # Check if answer already attempt exist or not
    existing_attempts = QuizAttempt.query.filter_by(
        attempt_quiz_id = quiz_id,
        attempt_participant_id=participant_id
    ).all()
    max_attempt_num = 0

    # no attempt exist it means first attempt
    if not existing_attempts:
        attempt = QuizAttempt(
            attempt_id = generate_user_id(),
            attempt_quiz_id=quiz_id,
            attempt_participant_id=participant_id,
            attempt_start_time=datetime.now(),
            attempt_status='In Progress',
            attempt_num = 1
        )
        db.session.add(attempt)
        #db.session.flush()
        db.session.commit()

        return render_template('participant_pages/attempt1.html',quiz=quiz,participant=participant,questions=questions)
    else:
        #find the maximum number of attempt. If it is more than allowed attempt then send the error message
        for attempt in existing_attempts:
            if attempt.attempt_num is not None and attempt.attempt_num > max_attempt_num:
                max_attempt_num = attempt.attempt_num
        if max_attempt_num < quiz.quiz_num_allowed_attempt:
            return render_template('participant_pages/attempt1.html',quiz=quiz,participant=participant,questions=questions)
        
        flash('There is no more attempt left for you in this quiz', 'danger')
        participant = Participants.query.filter_by(participant_id = participant_id).first()
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
        


@quiz_bp.route('/submit/<quiz_id>/<participant_id>', methods=['POST'])
def submit_quiz_json(quiz_id, participant_id):
    try:
        data = request.get_json()
        #fix
        quiz_id = int(quiz_id)
        participant_id = int(participant_id)

        if not data:
            return jsonify({'error': 'No data provided'}), 400
        start_time_str = data.get('start_time')
        submit_time_str = data.get('submit_time')
        time_taken = data.get('time_taken')
        # Parse timestamps
        start_time = datetime.fromisoformat(start_time_str)
        end_time = datetime.fromisoformat(submit_time_str)

        #find all attempts to find the previous maximum attempt number
        all_attempts = QuizAttempt.query.filter_by(
            attempt_quiz_id=quiz_id,
            attempt_participant_id=participant_id,
            attempt_status='Completed'
        ).all()
        
        if all_attempts:
            max_attempt_num = 0
            for attempt in all_attempts:
                if attempt.attempt_num is not None and attempt.attempt_num > max_attempt_num:
                    max_attempt_num = attempt.attempt_num
        else:
            max_attempt_num = 0

        current_attempt_num = max_attempt_num + 1
        # Find existing attempt or create new one
        attempt = QuizAttempt.query.filter_by(
            attempt_quiz_id=quiz_id,
            attempt_participant_id=participant_id,
            attempt_status='In Progress'
        ).first()
        
        # if the status is in-progress, that attempted will not be counted
        if not attempt:
            # Create new attempt if not exists
            attempt = QuizAttempt(
                attempt_id = generate_user_id(),
                attempt_quiz_id=quiz_id,
                attempt_participant_id=participant_id,
                attempt_start_time=start_time,
                attempt_status='In Progress'
            )
            db.session.add(attempt)
            #db.session.flush()  # Get the attempt_id
            db.session.commit()
        
        # Update attempt with provided end time and time taken
        attempt.attempt_end_time = end_time
        attempt.attempt_quiz_time_taken = time_taken  # If this field exists in your model
        attempt.attempt_status = 'Completed'
        attempt.attempt_num = current_attempt_num
        # Process answers
        correct_count = 0
        wrong_count = 0
        total_score = 0
        
        for answer_data in data.get('answers', []):
            question_id = answer_data['question_id']
            selected_option = answer_data['selected_option']
            
            # Get question details for scoring
            question = Questions.query.get(question_id)
            if not question:
                continue
            
            # Check if answer already exists (for auto-saved answers)
            existing_answer = ParticipantAnswer.query.filter_by(
                participant_answer_attempt_id=attempt.attempt_id,
                participant_answer_question_id=question_id
            ).first()
            
            # Determine if answer is correct
            is_correct = (str(selected_option).lower() == str(question.question_correct_option).lower())
            
            if existing_answer:
                # Update existing answer
                existing_answer.participant_answer_selected_option = selected_option
                existing_answer.participant_answer_timestamp = datetime.now()
                existing_answer.participant_answer_correct_answer = is_correct
            else:
                # Create new answer record
                participant_answer = ParticipantAnswer(
                    participant_answer_id = generate_user_id(),
                    participant_answer_attempt_id=attempt.attempt_id,
                    participant_answer_question_id=question_id,
                    participant_answer_selected_option=selected_option,
                    participant_answer_timestamp=datetime.now(),
                    participant_answer_correct_answer=is_correct,
                    participant_answer_selected_answer=question.question_correct_answer
                )
                db.session.add(participant_answer)
                db.session.commit()
            
            # Update scoring
            if is_correct:
                correct_count += 1
                total_score += question.question_mark
            else:
                wrong_count += 1
                # Apply negative marking if applicable
                if question.question_negative_mark > 0:
                    total_score -= question.question_negative_mark
        
        # Calculate unanswered questions
        total_questions = len(data.get('answers', []))
        # You might want to get actual total questions from quiz
        #from your_models import Quiz
        quiz = Quizzes.query.get(quiz_id)
        actual_total_questions = quiz.quiz_num_questions if quiz else total_questions
        unanswered_count = actual_total_questions - total_questions
        
        # Update attempt statistics
        attempt.attempt_score = max(0, total_score)  # Ensure score is not negative
        attempt.attempt_total_marks = quiz.quiz_num_questions * quiz.quiz_marks_per_question if quiz else 0
        attempt.attempt_correct_answers = correct_count
        attempt.attempt_wrong_answers = wrong_count
        attempt.attempt_unanswered_questions = unanswered_count
        # Commit all changes
        db.session.commit()
        print('submit_quiz-ok')
        return jsonify({
            'success': True,
            'attempt_id': attempt.attempt_id,
            'score': attempt.attempt_score,
            'total_marks': attempt.attempt_total_marks,
            'correct_answers': correct_count,
            'wrong_answers': wrong_count,
            'unanswered_questions': unanswered_count,
            'redirect_url': f'/quiz/results/{attempt.attempt_id}/{participant_id}'
        })
        
    except Exception as e:
        db.session.rollback()
        print('submit_error',str(e))
        return jsonify({'error': str(e)}), 500


@quiz_bp.route('/auto-save/<quiz_id>/<participant_id>', methods=['POST'])
def auto_save_answer(quiz_id, participant_id):
    try:
        data = request.get_json()
        
        if not data or 'answer' not in data:
            return jsonify({'error': 'No answer data provided'}), 400
        print('data',data)
        # Find or create attempt
        attempt = QuizAttempt.query.filter_by(
            attempt_quiz_id=quiz_id,
            attempt_participant_id=participant_id,
            attempt_status='In Progress'
        ).first()
        
        if not attempt:
            attempt = QuizAttempt(
                attempt_id = generate_user_id(),
                attempt_quiz_id=quiz_id,
                attempt_participant_id=participant_id,
                attempt_start_time=datetime.now(),
                attempt_status='In Progress'
            )
            db.session.add(attempt)
            db.session.commit()
        
        answer_data = data['answer']
        question_id = answer_data['question_id']
        selected_option = answer_data['selected_option']
        print("auto save")
        print(answer_data,question_id,selected_option)
        
        # Check if answer already exists
        existing_answer = ParticipantAnswer.query.filter_by(
            participant_answer_attempt_id=attempt.attempt_id,
            participant_answer_question_id=question_id
        ).first()
        
        # Get question for correctness check
        question = Questions.query.get(question_id)
        if question:
            is_correct = str(selected_option).lower() == str(question.question_correct_option).lower()
        else:
            is_correct = False
        actual_correct_answer = question.question_correct_answer
        if existing_answer:
            # Update existing answer
            existing_answer.participant_answer_selected_option = selected_option
            existing_answer.participant_answer_timestamp = datetime.now()
            existing_answer.participant_answer_correct_answer = is_correct
            existing_answer.participant_answer_selected_answer = actual_correct_answer
            db.session.add(existing_answer)
            db.session.commit()
        else:
            # Create new answer
            participant_answer = ParticipantAnswer(
                participant_answer_id = generate_user_id(),
                participant_answer_attempt_id=attempt.attempt_id,
                participant_answer_question_id=question_id,
                participant_answer_selected_option=selected_option,
                participant_answer_timestamp=datetime.now(),
                participant_answer_correct_answer=is_correct,
                participant_answer_selected_answer = actual_correct_answer
            )
            db.session.add(participant_answer)
            db.session.commit()
        
        db.session.commit()
        print('auto_save_success')
        return jsonify({'success': True, 'message': 'Answer auto-saved'})
        
    except Exception as e:
        db.session.rollback()
        print(str(e))
        return jsonify({'error': str(e)}), 500

@quiz_bp.route('/quiz/auto-save-all/<int:quiz_id>/<int:participant_id>', methods=['POST'])
def auto_save_all_answers(quiz_id, participant_id):
    try:
        data = request.get_json()
        
        if not data or 'answers' not in data:
            return jsonify({'error': 'No answers data provided'}), 400
        
        # Find or create attempt
        attempt = QuizAttempt.query.filter_by(
            attempt_quiz_id=quiz_id,
            attempt_participant_id=participant_id,
            attempt_status='In Progress'
        ).first()
        
        if not attempt:
            attempt = QuizAttempt(
                attempt_quiz_id=quiz_id,
                attempt_participant_id=participant_id,
                attempt_start_time=datetime.now(),
                attempt_status='In Progress'
            )
            db.session.add(attempt)
            #db.session.flush()
            db.session.commit()
        
        # Process all answers
        saved_count = 0
        for answer_data in data['answers']:
            question_id = answer_data['question_id']
            selected_option = answer_data['selected_option']
            
            # Check if answer already exists
            existing_answer = ParticipantAnswer.query.filter_by(
                attempt_id=attempt.attempt_id,
                question_id=question_id
            ).first()
            
            # Get question for correctness check
            question = Questions.query.get(question_id)
            is_correct = (selected_option == question.question_correct_option) if question else False
            
            if existing_answer:
                existing_answer.selected_option = selected_option
                existing_answer.answer_timestamp = datetime.now()
                existing_answer.correct_answer = is_correct
            else:
                participant_answer = ParticipantAnswer(
                    attempt_id=attempt.attempt_id,
                    question_id=question_id,
                    selected_option=selected_option,
                    answer_timestamp=datetime.now(),
                    correct_answer=is_correct
                )
                db.session.add(participant_answer)
                db.session.commit()
            saved_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'{saved_count} answers auto-saved'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@quiz_bp.route('/results/<int:attempt_id>/<int:participant_id>')
def quiz_results(attempt_id,participant_id):
    # Get the quiz attempt with quiz data in one query
    all_attempt_data = db.session.query(
            QuizAttempt, Quizzes, Participants
        ).join(
            Quizzes, QuizAttempt.attempt_quiz_id == Quizzes.quiz_id
        ).join(
            Participants, QuizAttempt.attempt_participant_id == Participants.participant_id
        ).all()
    
    # For specific attempt
    attempt_data = db.session.query(QuizAttempt, Quizzes).filter(
        QuizAttempt.attempt_quiz_id == Quizzes.quiz_id,
        QuizAttempt.attempt_id == attempt_id
    ).first()

    attempt, quiz = attempt_data
    print('attempt')
    print(attempt)
    print('quiz')
    print(quiz)
    # Calculate percentage with better error handling
    if attempt.attempt_total_marks and attempt.attempt_total_marks > 0:
        percentage = round((attempt.attempt_score / attempt.attempt_total_marks) * 100, 2)
    else:
        percentage = 0
    
    # Determine performance class and message
    if percentage >= 90:
        score_class = 'excellent'
        performance_message = 'Outstanding Performance! 🌟'
    elif percentage >= 75:
        score_class = 'good'
        performance_message = 'Great Job! 👏'
    elif percentage >= 60:
        score_class = 'average'
        performance_message = 'Good Effort! 👍'
    else:
        score_class = 'poor'
        performance_message = 'Keep Practicing! 💪'
    
    # Calculate time taken
    time_taken = "N/A"
    if attempt.attempt_start_time and attempt.attempt_end_time:
        time_diff = attempt.attempt_end_time - attempt.attempt_start_time
        hours, remainder = divmod(time_diff.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        time_taken = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
    
    # Get detailed answers with better query structure
    show_detailed_review = True
    participant_answers = []
    
    if show_detailed_review:
        participant_answers = db.session.query(
            ParticipantAnswer, Questions
        ).join(
            Questions, 
            ParticipantAnswer.participant_answer_question_id == Questions.question_id
        ).filter(
            ParticipantAnswer.participant_answer_attempt_id == attempt_id
        ).order_by(Questions.question_id).all()  # Added ordering for consistency
    print('res-quiz_id',participant_id,quiz.quiz_id)       
    return render_template('participant_pages/quiz_results.html',
                         attempt=attempt,
                         quiz=quiz,
                         percentage=percentage,
                         score_class=score_class,
                         performance_message=performance_message,
                         time_taken=time_taken,
                         show_detailed_review=show_detailed_review,
                         participant_answers=participant_answers,participant_id=participant_id)


@quiz_bp.route('/get_participant_attempts/<int:participant_id>/<int:quiz_id>', methods=['GET'])
def get_participant_attempts(participant_id, quiz_id):
    try:
        print('attemts-quiz_id',participant_id,quiz_id)
        attempts = QuizAttempt.query.filter_by(
            attempt_participant_id=participant_id,
            attempt_quiz_id=quiz_id
        ).order_by(QuizAttempt.attempt_num.asc()).all()
        
        attempts_data = []
        for attempt in attempts:
            attempts_data.append({
                'attempt_id': str(attempt.attempt_id),
                'attempt_num': attempt.attempt_num,
                'attempt_status': attempt.attempt_status,
                'attempt_start_time': attempt.attempt_start_time.isoformat() if attempt.attempt_start_time else None,
                'attempt_quiz_time_taken':attempt.attempt_quiz_time_taken,
                'attempt_score': attempt.attempt_score,
                'attempt_total_marks': attempt.attempt_total_marks,
                'attempt_correct_answers': attempt.attempt_correct_answers,
                'attempt_wrong_answers': attempt.attempt_wrong_answers,
                'attempt_unanswered_questions': attempt.attempt_unanswered_questions
            })
        #print(attempts_data)
        return jsonify({
            'success': True,
            'attempts': attempts_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@quiz_bp.route('/get_attempt_stats/<int:attempt_id>', methods=['GET'])
def get_attempt_stats(attempt_id):
    try:
        print('attempt_id entry',attempt_id)
        attempt = QuizAttempt.query.filter_by(attempt_id=attempt_id).first()
        
        # Check if attempt exists
        if not attempt:
            return jsonify({
                'success': False,
                'error': 'Attempt not found'
            }), 404
        
        # Calculate percentage
        percentage = 0
        if attempt.attempt_total_marks and attempt.attempt_total_marks > 0:
            percentage = round((attempt.attempt_score / attempt.attempt_total_marks) * 100, 2)
        
        # Calculate time taken in readable format
        time_taken = "N/A"
        if attempt.attempt_start_time and attempt.attempt_end_time:
            time_diff = attempt.attempt_end_time - attempt.attempt_start_time
            hours, remainder = divmod(time_diff.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            time_taken = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
        
        # Return single attempt data (not in array)
        attempt_data = {
            'attempt_id': attempt.attempt_id,
            'attempt_num': attempt.attempt_num,
            'attempt_status': attempt.attempt_status,
            'attempt_start_time': attempt.attempt_start_time.isoformat() if attempt.attempt_start_time else None,
            'attempt_quiz_time_taken': attempt.attempt_quiz_time_taken,
            'time_taken': time_taken,  # Formatted time
            'attempt_score': attempt.attempt_score,
            'attempt_total_marks': attempt.attempt_total_marks,
            'percentage': percentage,  # Calculated percentage
            'attempt_correct_answers': attempt.attempt_correct_answers,
            'attempt_wrong_answers': attempt.attempt_wrong_answers,
            'attempt_unanswered_questions': attempt.attempt_unanswered_questions
        }
        #print('attempt_data',attempt_data[attempt_id])
        print(attempt_data)
        return jsonify({
            'success': True,
            'singleAttemptData': attempt_data
        })
    except Exception as e:
        print(f"Error in get_attempt_stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

