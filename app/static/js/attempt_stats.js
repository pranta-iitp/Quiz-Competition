// Global variables
//var currentParticipantId = null;
let currentParticipantId = null;
let currentQuizId = null;

document.addEventListener('DOMContentLoaded', function() {
    // Debug the hidden field values
    const participantElement = document.getElementById('participant_id');
    const quizElement = document.getElementById('quiz_id');
    
    console.log('Participant element:', participantElement);
    console.log('Quiz element:', quizElement);
    console.log('Participant value (raw):', participantElement ? participantElement.value : 'Element not found');
    console.log('Quiz value (raw):', quizElement ? quizElement.value : 'Element not found');
    
    currentParticipantId = participantElement.value;
    currentQuizId = quizElement.value;

    console.log('Parsed Participant ID:', currentParticipantId);
    console.log('Parsed Quiz ID:', currentQuizId);
    console.log('Are they numbers?', !isNaN(currentParticipantId), !isNaN(currentQuizId));
    

    
    loadAttemptButtons();
});


function loadAttemptButtons() {
    console.log(currentParticipantId,currentQuizId);
    fetch(`/quiz/get_participant_attempts/${currentParticipantId}/${currentQuizId}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(function(response) {
        if (response.ok) {
            return response.json();
        }
        throw new Error('Network response was not ok');
    })
    .then(function(data) {
        renderAttemptButtons(data);
    })
    .catch(function(error) {
        console.error('Error loading attempts:', error);
        handleError('Failed to load attempts');
    });
}

// Render attempt buttons
function renderAttemptButtons(data) {
    //console.log(data);
    let attempts = data.attempts;
    var container = document.getElementById('attempt-buttons-container');
    container.innerHTML = '';
    var attempt = null;
    var button = null;
    for (var i = 0; i < attempts.length; i++) {
        attempt = attempts[i];
        console.log(attempt);
        button = document.createElement('button');
        button.className = 'btn btn-outline-primary me-2 mb-2';
        button.textContent = 'Attempt ' + attempt.attempt_num;
        console.log('button.textContent:'+button.textContent);
        button.setAttribute('data-attempt-id', attempt.attempt_id);
        
        // Use closure to capture the correct attempt_id
        button.onclick = (function(attemptId) {
            return function() {
                loadAttemptStats(attemptId);
                setActiveButton(this);
            };
        })(attempt.attempt_id);
        
        container.appendChild(button);
    }
    
    // Load first attempt by default if available
    if (attempts.length > 0) {
        loadAttemptStats(attempts[0].attempt_id);
        setActiveButton(container.firstChild);
    }
}

// Set active button styling
function setActiveButton(activeButton) {
    var buttons = document.querySelectorAll('#attempt-buttons-container button');
    for (var i = 0; i < buttons.length; i++) {
        buttons[i].classList.remove('btn-primary');
        buttons[i].classList.add('btn-outline-primary');
    }
    
    activeButton.classList.remove('btn-outline-primary');
    activeButton.classList.add('btn-primary');
}

// Load attempt statistics using fetch API
function loadAttemptStats(attemptId) {
    console.log('attemptId:'+attemptId);
    // Show loading spinner
    var loadingSpinner = document.getElementById('loading-spinner');
    var statsTable = document.getElementById('stats-table');
    
    if (loadingSpinner) loadingSpinner.style.display = 'block';
    if (statsTable) statsTable.style.display = 'none';
    
    fetch(`/quiz/get_attempt_stats/${attemptId}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(function(response) {
        if (response.ok) {
            return response.json();
        }
        throw new Error('Network response was not ok');
    })
    .then(function(data) {
        displayAttemptStats(data.singleAttemptData);
    })
    .catch(function(error) {
        console.error('Error loading attempt stats:', error);
        hideLoadingSpinner();
        handleError('Failed to load attempt statistics');
    });
}

// Display attempt statistics in the table
function displayAttemptStats(data) {
    var attemptNumEl = document.getElementById('attempt-num');
    var attemptStatusEl = document.getElementById('attempt-status');
    var timeTakenEl = document.getElementById('time-taken');
    var scoreEl = document.getElementById('score');
    var percentageEl = document.getElementById('percentage');
    var correctAnswersEl = document.getElementById('correct-answers');
    var wrongAnswersEl = document.getElementById('wrong-answers');
    var unansweredQuestionsEl = document.getElementById('unanswered-questions');
    
    if (attemptNumEl) attemptNumEl.textContent = data.attempt_num || '-';
    if (attemptStatusEl) attemptStatusEl.textContent = data.attempt_status || '-';
    if (timeTakenEl) timeTakenEl.textContent = data.time_taken || '-';
    if (scoreEl) scoreEl.textContent = (data.attempt_score || 0) + '/' + (data.attempt_total_marks || 0);
    if (percentageEl) percentageEl.textContent = (data.percentage || 0) + '%';
    if (correctAnswersEl) correctAnswersEl.textContent = data.attempt_correct_answers || 0;
    if (wrongAnswersEl) wrongAnswersEl.textContent = data.attempt_wrong_answers || 0;
    if (unansweredQuestionsEl) unansweredQuestionsEl.textContent = data.attempt_unanswered_questions || 0;
    
    hideLoadingSpinner();
}

// Helper function to hide loading spinner and show table
function hideLoadingSpinner() {
    var loadingSpinner = document.getElementById('loading-spinner');
    var statsTable = document.getElementById('stats-table');
    
    if (loadingSpinner) loadingSpinner.style.display = 'none';
    if (statsTable) statsTable.style.display = 'table';
}

// Error handling function
function handleError(message) {
    console.error('Attempt Stats Error:', message);
    hideLoadingSpinner();
    
    var container = document.getElementById('stats-container');
    if (container) {
        container.innerHTML = '<div class="alert alert-danger">Error loading attempt statistics. Please try again.</div>';
    }
}

// Initialize on page load
function initAttemptStatsOnLoad(participantId, quizId) {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            initializeAttemptStats(participantId, quizId);
        });
    } else {
        initializeAttemptStats(participantId, quizId);
    }
}
