document.addEventListener('DOMContentLoaded', () => {
  const checkboxes = document.querySelectorAll('.js-correct-checkbox');

  checkboxes.forEach(item => {
    item.addEventListener('change', event => {
      const answerId = item.dataset.answerId;
      const questionId = item.dataset.questionId;

      fetch('/correct/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': CSRF_TOKEN
        },
        body: `answer_id=${answerId}`
      })
        .then(response => {
          if (response.ok) {
            return response.json();
          }
          throw new Error('Permission denied');
        })
        .then(data => {
          if (data.status === true) {
            document.querySelectorAll(`.js-correct-checkbox[data-question-id="${questionId}"]`).forEach(box => {
              if (box !== item) box.checked = false;
            });
          }
        })
        .catch(error => {
          console.error(`Error: ${error}`);
          item.checked = !item.checked;
          alert('Error: ' + error.message);
        });
    });
  });
});
