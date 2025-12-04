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
  return cookieValue;
};

const csrfToken = getCookie('csrftoken');

document.querySelectorAll('.js-vote').forEach(btn => {
  btn.addEventListener('click', event => {
    event.preventDefault();
    const container = btn.closest('.js-vote-container');
    const objectId = container.dataset.id;
    const objectType = container.dataset.type;
    const voteType = btn.dataset.voteType;
    const counter = container.querySelector('.vote-count');

    fetch('/vote/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': csrfToken
      },
      body: `object_id=${objectId}&object_type=${objectType}&vote_type=${voteType}`
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
      body: `answer_id=${answerId}`
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

function debounce(func, wait) {
  let timeout;
  return function(...args) {
    const context = this;
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(context, args), wait);
  };
};

const searchInput = document.getElementById('search-input');
const searchResults = document.getElementById('search-results');

if (searchInput) {
  searchInput.addEventListener('input', debounce((e) => {
    const query = e.target.value.trim();

    if (query.length < 2) {
      searchResults.innerHTML = '';
      searchResults.classList.remove('active');
      return;
    }

    fetch(`/search/suggestions/?q=${encodeURIComponent(query)}`)
      .then(response => response.json())
      .then(data => {
        searchResults.innerHTML = '';
        
        if (data.results.length > 0) {
          data.results.forEach(item => {
            const link = document.createElement('a');
            link.href = item.url;
            link.className = 'search-result-item';
            link.innerText = item.title;
            searchResults.appendChild(link);
          });
          searchResults.classList.add('active');
        } else {
          searchResults.classList.remove('active');
        }
      })
      .catch(error => console.error('Search error:', error));
  }, 300));

  document.addEventListener('click', (e) => {
    if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
      searchResults.classList.remove('active');
    }
  });
};
