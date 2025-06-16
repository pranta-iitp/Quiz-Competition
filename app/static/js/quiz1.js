// quiz.js (Simplified)
// Global state
let totalQuestions = 0;  // Initialize as 0
let currentQuestion = 1;
let answeredQuestions = new Set();
let timeRemaining = 0;   // Initialize as 0
let quizTimer = null;
let quizAnswers = {};

// Function to disable all buttons except start quiz button
function disableAllButtonsExceptStart() {
    // Disable navigation buttons
    var prevBtn = document.getElementById('prev-btn');
    var nextBtn = document.getElementById('next-btn');
    var submitBtn = document.getElementById('submit-btn');
    
    if (prevBtn) prevBtn.disabled = true;
    if (nextBtn) nextBtn.disabled = true;
    if (submitBtn) submitBtn.disabled = true;
    
    // Disable question navigation buttons
    var questionNavBtns = document.querySelectorAll('.question-nav-btn');
    for (var i = 0; i < questionNavBtns.length; i++) {
        questionNavBtns[i].disabled = true;
    }
    
    // Disable clear selection buttons
    var clearBtns = document.querySelectorAll('[onclick*="clearSelection"]');
    for (var i = 0; i < clearBtns.length; i++) {
        clearBtns[i].disabled = true;
    }
    
    // Disable all radio buttons
    var radioButtons = document.querySelectorAll('input[type="radio"]');
    for (var i = 0; i < radioButtons.length; i++) {
        radioButtons[i].disabled = true;
    }
}
// Function to enable all quiz buttons
function enableAllQuizButtons() {
    // Enable navigation buttons (they'll be managed by existing logic)
    var prevBtn = document.getElementById('prev-btn');
    var nextBtn = document.getElementById('next-btn');
    var submitBtn = document.getElementById('submit-btn');
    
    if (prevBtn) prevBtn.disabled = false;
    if (nextBtn) nextBtn.disabled = false;
    if (submitBtn) submitBtn.disabled = false;
    
    // Enable question navigation buttons
    var questionNavBtns = document.querySelectorAll('.question-nav-btn');
    for (var i = 0; i < questionNavBtns.length; i++) {
        questionNavBtns[i].disabled = false;
    }
    
    // Enable clear selection buttons
    var clearBtns = document.querySelectorAll('[onclick*="clearSelection"]');
    for (var i = 0; i < clearBtns.length; i++) {
        clearBtns[i].disabled = false;
    }
    
    // Enable all radio buttons
    var radioButtons = document.querySelectorAll('input[type="radio"]');
    for (var i = 0; i < radioButtons.length; i++) {
        radioButtons[i].disabled = false;
    }
}



document.addEventListener('DOMContentLoaded', function() {

     // Initialize values after DOM is ready
     totalQuestions = parseInt(document.getElementById('total-questions').value, 10);
     timeRemaining = parseInt(document.getElementById('quiz-duration').value, 10);
    
    // Hide timer initially
    const timerSection = document.getElementById('timer-section');
    if (timerSection) {
        timerSection.style.display = 'none';
    }

    disableAllButtonsExceptStart();
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

// Fixed: Use correct IDs from HTML
    const startButton = document.getElementById('start-quiz-btn');
    if (startButton) {
        startButton.addEventListener('click', function () {
            const quizContent = document.getElementById('quiz-content'); // Correct ID
            const startWrapper = document.getElementById('start-quiz-wrapper'); // Correct ID
            const timerSection = document.getElementById('timer-section');

            // Hide the start button wrapper and show the quiz content
            if (startWrapper) startWrapper.style.display = 'none';
            if (quizContent) quizContent.style.display = 'block';
            if (timerSection) timerSection.style.display = 'block';

            showQuestion(1);  // Show first question
            updateProgressBar();
            startTimer();     // Start the timer
            enableAllQuizButtons();
            quizStartTime = new Date();
            
            // Set the start time in the hidden field
            const startTimeField = document.getElementById('quiz-start-time');
            if (startTimeField) {
                startTimeField.value = quizStartTime.toISOString();
            }
        });
    }

    updateQuestionNavigation();
    updateProgressBar();
    //startTimer();
    
    // Add event delegation for radio buttons as backup
    setupRadioEventHandlers();
});


// Handle radio button changes
function setupRadioEventHandlers() {
    document.addEventListener('change', function(event) {
        if (event.target.type === 'radio' && event.target.name.startsWith('question_')) {
            const questionId = event.target.name.replace('question_', '');
            const selectedValue = event.target.value;
            quizAnswers[questionId] = {
                question_id: questionId,
                selected_option: selectedValue,
                timestamp: new Date().toISOString()
            };
            answeredQuestions.add(parseInt(questionId));
            updateProgressBar();
            autoSaveAnswer(questionId);
        }
    });
}

// Auto-save answer for a question
function autoSaveAnswer(questionId) {
    const quizId = document.getElementById('quiz-id').value;
    const participantId = document.getElementById('participant-id').value;
    const answerData = {
        quiz_id: quizId,
        participant_id: participantId,
        answer: quizAnswers[questionId]
    };
    fetch(`/quiz/auto-save/${quizId}/${participantId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
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
    
    const submitTime = new Date();
    const timeTakenSeconds = Math.floor((submitTime - quizStartTime) / 1000); // difference in seconds

    const submitData = {
        quiz_id: parseInt(quizId),
        participant_id: parseInt(participantId),
        answers: Object.values(quizAnswers),
        start_time: quizStartTime ? quizStartTime.toISOString() : null,
        submit_time: submitTime.toISOString(),
        time_taken: timeTakenSeconds
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