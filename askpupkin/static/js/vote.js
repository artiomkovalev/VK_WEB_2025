document.addEventListener('click', (event) => {
  const btn = event.target.closest('.js-vote');
  if (!btn) return;

  event.preventDefault();

  const container = btn.closest('.js-vote-container');
  const objectId = container.dataset.id;
  const objectType = container.dataset.type;
  const voteType = btn.dataset.voteType;
  const counter = container.querySelector('.vote-count');

  const url = `/${objectType}/${objectId}/vote/`;

  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-CSRFToken': CSRF_TOKEN
    },
    body: `vote_type=${voteType}`
  })
    .then(async response => {
      if (response.status === 401) {
        window.location.href = `/login/?next=${window.location.pathname}`;
        return;
      }
      if (response.ok) {
        return response.json();
      }
      const errorData = await response.json();
      throw new Error(errorData.error || 'Network response wasn\'t ok');
    })
    .then(data => {
      if (data) {
        counter.innerText = data.rating;

        if (btn.classList.contains('active')) {
          btn.classList.remove('active');
        } else {
          container.querySelectorAll('.js-vote').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
        }
      }
    })
    .catch(error => {
      console.error(`Error: ${error}`);
      alert(error.message);
    });
});
