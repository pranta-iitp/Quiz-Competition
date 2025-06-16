// Ensure all functions are global
window.loadQuizzes = function(section) {
  const quizAuthorId = document.getElementById('author-id').value;
  const container = document.getElementById('quizzes-table-container');
  container.innerHTML = '<div class="text-center text-muted">Loading quizzes...</div>';

  fetch(`/author/get_quiz/${quizAuthorId}/${section}`)
    .then(response => response.json())
    .then(data => {
        data = data.allQuizData;
        console.log('quizzes front-end'+data);
        //data = 
      if (data && data.length > 0) {
        window.renderQuizTable(data, container,quizAuthorId);
      } else {
        container.innerHTML = `<div class="alert alert-info text-center">No ${section.toLowerCase()} quizzes found.</div>`;
      }
    })
    .catch(error => {
      container.innerHTML = `<div class="alert alert-danger text-center">Failed to load quizzes.</div>`;
      console.error('Error fetching quizzes:', error);
    });
};

window.renderQuizTable = function(quizzes, container,quizAuthorId) {
    console.log('quizzes front-end'+quizzes);
  let table = `
    <table class="table table-bordered table-hover">
      <thead class="table-light">
        <tr>
          <th>Quiz Title</th>
          <th>Number of Questions</th>
          <th>Mark per question</th>
          <th>Negative Mark per question</th>
          <th>Total Mark</th>
          <th>Created On</th>
          
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
  `;
  quizzes.forEach(quiz => {
    table += `
      <tr>
        <td>${quiz.quiz_title}</td>
        <td>${quiz.question_count || 0}</td>
        <td>${quiz.quiz_mark_per_question || 0}</td>
        <td>${quiz.quiz_negative_mark_per_question || 0}</td>
        <td>${quiz.quiz_maximum_marks || 0}</td>
        <td>${quiz.created_on || '-'}</td>
        
        <td>
          <button class="btn btn-sm btn-outline-primary" onclick="viewQuiz('${quiz.quiz_id}','${quizAuthorId}')">View</button>
          <button class="btn btn-sm btn-outline-secondary" onclick="editQuiz('${quiz.quiz_id}','${quizAuthorId}')">Edit</button>
        </td>
      </tr>
    `;
  });
  table += '</tbody></table>';
  container.innerHTML = table;
};

window.viewQuiz = function(quizId,quizAuthorId) {
  alert('View Quiz: ' + quizId+' '+quizAuthorId);
  window.open(`/quiz/view_questions/${quizId}/${quizAuthorId}`, '_blank');
};

window.editQuiz = function(quizId,quizAuthorId) {
  //alert('Edit Quiz: ' + quizId+' '+quizAuthorId);
  window.open(`/quiz/create_questions/${quizId}/${quizAuthorId}`, '_blank');
};

// Optionally, load default tab if needed
// window.loadQuizzes('Active');
