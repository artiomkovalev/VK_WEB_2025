function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      };
    };
  };
  return cookieValue
};

const csrfToken = getCookie('csrftoken');

document.querySelectorAll('.js-vote').forEach(item => {
  item.addEventListener('click', event => {
    event.preventDefault();
    
    const container = item.closest('.question-item');
    const questionId = container.dataset.questionId;
    const voteType = item.dataset.voteType;
    const counter = container.querySelector('.vote-count');

    fetch('/vote/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': csrfToken
      },
      body: `question_id=${questionId}&vote_type=${voteType}`
    })
    .then(response => {
      if (response.ok) {
        return response.json();
      };
      throw new Error('Network response wasn\'t ok');
    })
    .then(data => {
      counter.innerText = data.rating;
    })
    .catch(error => console.error(`Error: ${error}`));
  });
});

document.querySelectorAll('.js-correct-checkbox').forEach(item => {
  item.addEventListener('change', event => {
    const answerId = item.dataset.answerId;
    const questionId = item.dataset.questionId;

    fetch('/correct/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': csrfToken
      },
      body: `question_id=${questionId}&answer_id=${answerId}`
    })
    .then(response => {
      if (response.ok) {
        return response.json();
      };
      throw new Error('Permission denied');
    })
    .then(data => {
      if (data.status === true) {
        document.querySelectorAll(`.js-correct-checkbox[data-question-id="${questionId}"]`).forEach(box => {
          if (box !== item) box.checked = false;
        });
      };
    })
    .catch(error => {
      console.error(`Error: ${error}`);
      item.checked = !item.checked;
    });
  });
});
