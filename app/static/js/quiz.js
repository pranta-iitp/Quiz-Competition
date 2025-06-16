// quiz.js - Modified for JSON submission

// Get total questions from hidden input
const totalQuestions = parseInt(document.getElementById('total-questions').value, 10);
let currentQuestion = 1;
let answeredQuestions = new Set();
let timeRemaining = 2700; // 45 minutes in seconds
let quizTimer = null;

// Store answers in memory for JSON submission
let quizAnswers = {}; //global

// Auto-hide flash messages
document.addEventListener('DOMContentLoaded', function() {
    const flashMessage = document.getElementById('flash-message');
    if (flashMessage) {
        setTimeout(function() {
            flashMessage.classList.remove('show');
            flashMessage.classList.add('fade');
            setTimeout(function() {
                flashMessage.remove();
            }, 150);
        }, 2000);
    }

    updateQuestionNavigation();
    updateProgressBar();
    startTimer();
    
    // Add event delegation for radio buttons as backup
    setupRadioEventHandlers();
});

// Setup event delegation for radio buttons
function setupRadioEventHandlers() {
    document.addEventListener('change', function(event) {
        if (event.target.type === 'radio' && event.target.name.startsWith('question_')) {
            const questionId = event.target.name.replace('question_', '');
            const questionCard = event.target.closest('.question-card');
            
            if (questionCard) {
                const questionNumMatch = questionCard.id.match(/question-(\d+)/);
                if (questionNumMatch) {
                    const questionNum = parseInt(questionNumMatch[1]);
                    console.log('Event delegation triggered for:', questionNum, questionId);
                    
                    // Call the update function directly
                    handleAnswerUpdate(questionNum, parseInt(questionId), event.target.value);
                }
            }
        }
    });
}

// Direct answer update handler
function handleAnswerUpdate(questionNum, questionId, selectedValue) {
    console.log('handleAnswerUpdate called with:', questionNum, questionId, selectedValue);
    
    quizAnswers[questionId] = {
        question_id: questionId,
        selected_option: selectedValue,
        timestamp: new Date().toISOString()
    };

    console.log('Answer stored via event delegation:', quizAnswers[questionId]);

    answeredQuestions.add(questionNum);
    updateProgressBar();
    updateQuestionGrid();

    // Update visual styling
    const selectedRadio = document.querySelector(`input[name="question_${questionId}"][value="${selectedValue}"]`);
    if (selectedRadio) {
        const selectedLabel = selectedRadio.closest('.option-label');
        if (selectedLabel) {
            const allOptions = selectedLabel.parentElement.querySelectorAll('.option-label');
            allOptions.forEach(opt => opt.classList.remove('selected-option'));
            selectedLabel.classList.add('selected-option');
        }
    }

    autoSaveAnswer(questionId);
}

// Timer functions
function startTimer() {
    const timerSection = document.getElementById('timer-section');
    if (timerSection) {
        timerSection.style.display = 'block';
    }
    
    quizTimer = setInterval(function() {
        timeRemaining--;
        updateTimerDisplay();
        if (timeRemaining <= 300) {
            const timerElement = document.getElementById('timer');
            if (timerElement && timerElement.parentElement) {
                timerElement.parentElement.classList.add('timer-warning');
            }
        }
        if (timeRemaining <= 0) {
            alert('Time is up! Quiz will be auto-submitted.');
            submitQuiz();
        }
    }, 1000);
}

function updateTimerDisplay() {
    const timerElement = document.getElementById('timer');
    if (timerElement) {
        let minutes = Math.floor(timeRemaining / 60);
        let seconds = timeRemaining % 60;
        timerElement.textContent =
            String(minutes).padStart(2, '0') + ':' + String(seconds).padStart(2, '0');
    }
}

// Navigation functions
function nextQuestion() {
    if (currentQuestion < totalQuestions) {
        showQuestion(currentQuestion + 1);
    }
}

function previousQuestion() {
    if (currentQuestion > 1) {
        showQuestion(currentQuestion - 1);
    }
}

function showQuestion(questionNum) {
    // Hide current question
    const prevCard = document.getElementById(`question-${currentQuestion}`);
    if (prevCard) prevCard.style.display = 'none';

    // Show new question
    const newCard = document.getElementById(`question-${questionNum}`);
    if (newCard) newCard.style.display = 'block';

    currentQuestion = questionNum;

    updateQuestionNavigation();
    const currentQuestionElement = document.getElementById('current-question');
    if (currentQuestionElement) {
        currentQuestionElement.textContent = currentQuestion;
    }
}

function goToQuestion(questionNum) {
    showQuestion(questionNum);
}

function updateQuestionNavigation() {
    // Prev/Next buttons
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const submitBtn = document.getElementById('submit-btn');
    
    if (prevBtn) {
        prevBtn.disabled = (currentQuestion === 1);
    }

    if (currentQuestion === totalQuestions) {
        if (nextBtn) nextBtn.style.display = 'none';
        if (submitBtn) submitBtn.style.display = 'inline-block';
    } else {
        if (nextBtn) nextBtn.style.display = 'inline-block';
        if (submitBtn) submitBtn.style.display = 'none';
    }

    updateQuestionGrid();
}

function updateQuestionGrid() {
    const buttons = document.querySelectorAll('.question-nav-btn');
    buttons.forEach((btn) => {
        const questionNum = parseInt(btn.getAttribute('data-question'), 10);
        btn.className = 'btn btn-sm w-100 question-nav-btn ';
        if (questionNum === currentQuestion) {
            btn.className += 'btn-warning';
        } else if (answeredQuestions.has(questionNum)) {
            btn.className += 'btn-success';
        } else {
            btn.className += 'btn-outline-secondary';
        }
    });
}



function updateAnswerStatus(questionId) {
    // Find the selected radio button for this question
    var selectedOption = document.querySelector('input[name="question_' + questionId + '"]:checked');
    if (selectedOption) {
        var selectedValue = selectedOption.value;
        // Print the selected option and question id
        console.log('Question ID:', questionId, 'Selected Option:', selectedValue);
        // You can also update the UI or status here as needed
    } else {
        // No option selected (should not happen on change, but included for safety)
        console.log('Question ID:', questionId, 'No option selected');
    }
}



function updateAnswerStatus1(questionNum, questionId) {
    console.log('updateAnswerStatus called with:', questionNum, questionId);
    
    // Multiple attempts to find the selected option with different delays
    function checkForSelection(attempt = 0) {
        const selector = `input[name="question_${questionId}"]:checked`;
        //document.querySelector(`input[name="question_${questionId}"][value="${selectedValue}"]`);
        const selectedOption = document.querySelector(selector);
        
        console.log(`Attempt ${attempt + 1}: Selected option:`, selectedOption);

        if (selectedOption) {
            quizAnswers[questionId] = {
                question_id: questionId,
                selected_option: selectedOption.value,
                timestamp: new Date().toISOString()
            };

            console.log('Answer stored:', quizAnswers[questionId]);

            answeredQuestions.add(questionNum);
            updateProgressBar();
            updateQuestionGrid();

            // Update visual styling
            const selectedLabel = selectedOption.closest('.option-label');
            if (selectedLabel) {
                const allOptions = selectedLabel.parentElement.querySelectorAll('.option-label');
                allOptions.forEach(opt => opt.classList.remove('selected-option'));
                selectedLabel.classList.add('selected-option');
            }

            autoSaveAnswer(questionId);
        } else {
            // Try again with longer delay, up to 3 attempts
            if (attempt < 2) {
                console.log(`Retrying selection detection for question ${questionId}, attempt ${attempt + 2}`);
                setTimeout(() => checkForSelection(attempt + 1), (attempt + 1) * 50);
            } else {
                console.warn(`Failed to detect selection for question ID ${questionId} after 3 attempts`);
                // Debug: log all radio buttons for this question
                const allRadios = document.querySelectorAll(`input[name="question_${questionId}"]`);
                console.log('All radios for this question:', allRadios);
                allRadios.forEach((radio, index) => {
                    console.log(`Radio ${index}: value=${radio.value}, checked=${radio.checked}, id=${radio.id}`);
                });
            }
        }
    }
    
    // Start checking immediately, then with small delays if needed
    checkForSelection();
}

function clearSelection(questionId, questionNum) {
    console.log('clearSelection called for:', questionId, questionNum);
    
    const radios = document.querySelectorAll(`input[name="question_${questionId}"]`);
    radios.forEach(radio => {
        radio.checked = false;
        const label = radio.closest('.option-label');
        if (label) {
            label.classList.remove('selected-option');
        }
    });
    
    // Remove from memory
    delete quizAnswers[questionId];
    answeredQuestions.delete(questionNum);
    updateProgressBar();
    updateQuestionGrid();
}

function updateProgressBar() {
    const progressBar = document.getElementById('progress-bar');
    const answeredCount = document.getElementById('answered-count');
    
    if (progressBar) {
        const progress = (answeredQuestions.size / totalQuestions) * 100;
        progressBar.style.width = progress + '%';
    }
    
    if (answeredCount) {
        answeredCount.textContent = answeredQuestions.size;
    }
}

// Submit functions with JSON
function showSubmitModal() {
    const modalAnswered = document.getElementById('modal-answered');
    const modalUnanswered = document.getElementById('modal-unanswered');
    
    if (modalAnswered) modalAnswered.textContent = answeredQuestions.size;
    if (modalUnanswered) modalUnanswered.textContent = totalQuestions - answeredQuestions.size;

    const submitModal = document.getElementById('submitModal');
    if (submitModal && typeof bootstrap !== 'undefined') {
        const modal = new bootstrap.Modal(submitModal);
        modal.show();
    }
}

function submitQuiz() {
    if (quizTimer) {
        clearInterval(quizTimer);
    }
    
    // Prepare JSON data
    const quizIdElement = document.getElementById('quiz-id');
    const participantIdElement = document.getElementById('participant-id');
    
    if (!quizIdElement || !participantIdElement) {
        console.error('Missing quiz ID or participant ID elements');
        alert('Error: Missing required information. Please refresh and try again.');
        return;
    }
    
    const quizId = quizIdElement.value;
    const participantId = participantIdElement.value;
    
    const submitData = {
        quiz_id: parseInt(quizId),
        participant_id: parseInt(participantId),
        answers: Object.values(quizAnswers),
        submit_time: new Date().toISOString(),
        time_taken: 2700 - timeRemaining // Time taken in seconds
    };
    
    console.log('Submitting quiz data:', submitData);
    
    // Submit via fetch API
    fetch(`/quiz/submit/${quizId}/${participantId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(submitData)
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        }
        throw new Error('Network response was not ok');
    })
    .then(data => {
        // Redirect to results page or show success message
        if (data.redirect_url) {
            window.location.href = data.redirect_url;
        } else {
            alert('Quiz submitted successfully!');
            window.location.href = '/quiz/results/' + data.attempt_id;
        }
    })
    .catch(error => {
        console.error('Error submitting quiz:', error);
        alert('Error submitting quiz. Please try again.');
    });
}

// Auto-save individual answer
function autoSaveAnswer(questionId) {
    const quizIdElement = document.getElementById('quiz-id');
    const participantIdElement = document.getElementById('participant-id');
    
    if (!quizIdElement || !participantIdElement) {
        console.warn('Cannot auto-save: missing quiz ID or participant ID');
        return;
    }
    
    const quizId = quizIdElement.value;
    const participantId = participantIdElement.value;
    
    const answerData = {
        quiz_id: parseInt(quizId),
        participant_id: parseInt(participantId),
        answer: quizAnswers[questionId]
    };
    console.log('save'); 
    fetch(`/quiz/auto-save/${quizId}/${participantId}`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(answerData)
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        console.log('Auto-save successful!');
    } else {
        console.error('Auto-save error:', data.error || data.message);
    }
})
.catch(error => console.log('Auto-save failed:', error));

}

// Auto-save all answers every 30 seconds
function autoSaveAll() {
    if (Object.keys(quizAnswers).length > 0) {
        const quizIdElement = document.getElementById('quiz-id');
        const participantIdElement = document.getElementById('participant-id');
        
        if (!quizIdElement || !participantIdElement) {
            console.warn('Cannot auto-save all: missing quiz ID or participant ID');
            return;
        }
        
        const quizId = quizIdElement.value;
        const participantId = participantIdElement.value;
        
        const saveData = {
            quiz_id: parseInt(quizId),
            participant_id: parseInt(participantId),
            answers: Object.values(quizAnswers),
            save_time: new Date().toISOString()
        };
        
        fetch(`/quiz/auto-save-all/${quizId}/${participantId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(saveData)
        }).catch(error => console.log('Auto-save failed:', error));
    }
}

// Auto-save every 30 seconds
//setInterval(autoSaveAll, 30000);

// Expose functions to global scope for inline HTML event handlers
window.nextQuestion = nextQuestion;
window.previousQuestion = previousQuestion;
window.goToQuestion = goToQuestion;
window.updateAnswerStatus = updateAnswerStatus;
window.clearSelection = clearSelection;
window.showSubmitModal = showSubmitModal;
window.submitQuiz = submitQuiz;