document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.getElementById('search-input');
  const searchResults = document.getElementById('search-results');

  if (searchInput && searchResults) {
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

          if (data.results && data.results.length > 0) {
            data.results.forEach(item => {
              const link = document.createElement('a');
              link.href = item.url;
              link.className = 'search-result-item';
              link.innerText = item.title;
              searchResults.appendChild(link);
            });
          } else {
            const noRes = document.createElement('div');
            noRes.className = 'search-result-item';
            noRes.style.cursor = 'default';
            noRes.style.color = '#718096';
            noRes.innerText = 'No results found';
            searchResults.appendChild(noRes);
          };
          searchResults.classList.add('active');
        })
        .catch(error => console.error('Search error:', error));
    }, 300));

    document.addEventListener('click', (e) => {
      if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
        searchResults.classList.remove('active');
      }
    });
  }
});
