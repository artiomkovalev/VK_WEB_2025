document.addEventListener('change', (event) => {
  const item = event.target.closest('.js-correct-checkbox');

  if (!item) return;

  const answerId = item.dataset.answerId;
  const questionId = item.dataset.questionId;

  fetch('/correct/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': CSRF_TOKEN
    },
    body: JSON.stringify({ answer_id: answerId })
  })
    .then(response => {
      if (response.ok) {
        return response.json();
      }
      return response.json().then(err => { throw new Error(err.error || 'Error'); });
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
      alert(error.message);
    });
});
