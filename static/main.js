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
  // populate sources with persistence
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

    const STORAGE_CAT = 'news_source_category';
    const STORAGE_SELECTED = 'news_source_selected';
    const savedCat = localStorage.getItem(STORAGE_CAT);
    const savedSelected = JSON.parse(localStorage.getItem(STORAGE_SELECTED) || '[]');

    if (savedCat && Array.from(catEl.options).some(o => o.value === savedCat)) {
      catEl.value = savedCat;
    }

    function populateSourcesForCategory() {
      const cat = catEl.value;
      const list = sources[cat] || [];
      srcEl.innerHTML = '';
      for (const s of list) {
        const o = document.createElement('option');
        o.value = s;
        o.textContent = s;
        if (savedSelected.includes(s)) o.selected = true;
        srcEl.appendChild(o);
      }
      const currentSelected = Array.from(srcEl.selectedOptions).map(o => o.value);
      localStorage.setItem(STORAGE_SELECTED, JSON.stringify(currentSelected));
    }

    // when category changes, persist and repopulate
    catEl.addEventListener('change', () => {
      localStorage.setItem(STORAGE_CAT, catEl.value);
      populateSourcesForCategory();
    });

    // when selection changes, persist
    srcEl.addEventListener('change', () => {
      const sel = Array.from(srcEl.selectedOptions).map(o => o.value);
      localStorage.setItem(STORAGE_SELECTED, JSON.stringify(sel));
    });

    populateSourcesForCategory();

    document.getElementById('openSourceBtn').addEventListener('click', async () => {
      const category = catEl.value;
      const q = document.getElementById('q').value.trim() || '';
      const selected = Array.from(srcEl.selectedOptions).map(o => o.value);
      if (!selected.length) {
        alert('Please select one or more sources.');
        return;
      }
      // Open placeholder tabs synchronously to avoid popup blocking
      const tabs = selected.map(() => window.open('', '_blank', 'noopener'));
      try {
        const promises = selected.map(s =>
          fetch(`/api/source-search?category=${encodeURIComponent(category)}&source=${encodeURIComponent(s)}&q=${encodeURIComponent(q)}`)
            .then(r => r.json())
        );
        const results = await Promise.all(promises);
        for (let i = 0; i < results.length; i++) {
          const res = results[i];
          const tab = tabs[i];
          if (res && res.url) {
            try {
              if (tab) tab.location = res.url; else window.open(res.url, '_blank', 'noopener');
            } catch (e) {
              if (tab) tab.close();
              window.open(res.url, '_blank', 'noopener');
            }
          } else {
            if (tab) tab.close();
          }
        }
      } catch (e) {
        console.error('Error opening source searches', e);
        for (const t of tabs) if (t) t.close();
        alert('Could not open one or more source searches');
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
