async function fetchTop(country) {
  const params = new URLSearchParams();
  if (country) params.set('country', country);
  const res = await fetch('/api/top?' + params.toString());
  return res.json();
}

async function fetchSearch(q) {
  const params = new URLSearchParams({ q });
  const res = await fetch('/api/search?' + params.toString());
  return res.json();
}

function renderArticles(container, articles) {
  container.innerHTML = '';
  if (!articles || articles.length === 0) {
    container.textContent = 'No articles found.';
    return;
  }
  for (const a of articles) {
    const card = document.createElement('article');
    card.className = 'article';
    const img = a.urlToImage ? `<img src="${a.urlToImage}" alt=""/>` : '';
    card.innerHTML = `
      <h3><a href="${a.url}" target="_blank" rel="noopener">${a.title}</a></h3>
      <p class="meta">${a.source.name} · ${a.publishedAt ? new Date(a.publishedAt).toLocaleString() : ''}</p>
      ${img}
      <p>${a.description || ''}</p>
    `;
    container.appendChild(card);
  }
}

document.getElementById('searchBtn').addEventListener('click', async () => {
  const q = document.getElementById('q').value.trim();
  const results = document.getElementById('results');
  results.textContent = 'Loading...';
  try {
    const data = q ? await fetchSearch(q) : await fetchTop(document.getElementById('country').value);
    renderArticles(results, data.articles);
  } catch (e) {
    results.textContent = 'Error fetching articles.';
    console.error(e);
  }
});

document.getElementById('topBtn').addEventListener('click', async () => {
  const results = document.getElementById('results');
  results.textContent = 'Loading top stories...';
  try {
    const data = await fetchTop(document.getElementById('country').value);
    renderArticles(results, data.articles);
  } catch (e) {
    results.textContent = 'Error fetching top stories.';
    console.error(e);
  }
});

// Load top stories on first load
document.addEventListener('DOMContentLoaded', () => document.getElementById('topBtn').click());
