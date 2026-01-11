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

async function fetchSources() {
  const res = await fetch('/api/sources');
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
document.addEventListener('DOMContentLoaded', async () => {
  document.getElementById('topBtn').click();
  // populate sources
  try {
    const sources = await fetchSources();
    const catEl = document.getElementById('sourceCategory');
    const srcEl = document.getElementById('sourceSelect');
    catEl.innerHTML = '';
    for (const cat of Object.keys(sources)) {
      const opt = document.createElement('option');
      opt.value = cat;
      opt.textContent = cat;
      catEl.appendChild(opt);
    }
    function populateSourcesForCategory() {
      const cat = catEl.value;
      const list = sources[cat] || [];
      srcEl.innerHTML = '';
      for (const s of list) {
        const o = document.createElement('option');
        o.value = s;
        o.textContent = s;
        srcEl.appendChild(o);
      }
    }
    catEl.addEventListener('change', populateSourcesForCategory);
    populateSourcesForCategory();

    document.getElementById('openSourceBtn').addEventListener('click', async () => {
      const category = catEl.value;
      const source = srcEl.value;
      const q = document.getElementById('q').value.trim() || '';
      try {
        const res = await fetch(`/api/source-search?category=${encodeURIComponent(category)}&source=${encodeURIComponent(source)}&q=${encodeURIComponent(q)}`);
        const data = await res.json();
        if (data.url) window.open(data.url, '_blank', 'noopener');
      } catch (e) {
        console.error('Error opening source search', e);
        alert('Could not open source search');
      }
    });
  } catch (e) {
    console.error('Failed to load sources', e);
  }
});

// DPI / UI scaling: set base font-size according to devicePixelRatio and user slider
function applyDPIScaling() {
  const dpr = window.devicePixelRatio || 1;
  // base 16px scaled by device pixel ratio (clamped)
  const base = Math.max(12, Math.min(24, 16 * dpr));
  document.documentElement.style.setProperty('--base-font-size', base + 'px');
}

applyDPIScaling();

const scaleEl = document.getElementById('uiScale');
const scaleLabel = document.getElementById('uiScaleLabel');
if (scaleEl) {
  scaleEl.addEventListener('input', () => {
    const pct = Number(scaleEl.value);
    scaleLabel.textContent = pct + '%';
    const base = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--base-font-size')) || 16;
    const newBase = (base * pct) / 100;
    document.documentElement.style.setProperty('--base-font-size', newBase + 'px');
  });
}

// update scaling if devicePixelRatio changes (some displays support change)
window.matchMedia(`(resolution: ${window.devicePixelRatio}dppx)`).addEventListener?.('change', applyDPIScaling);
