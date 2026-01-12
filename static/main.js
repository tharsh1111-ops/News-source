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
    let savedSelected = JSON.parse(localStorage.getItem(STORAGE_SELECTED) || '[]');
    if (!Array.isArray(savedSelected)) savedSelected = [];

    if (savedCat && Array.from(catEl.options).some(o => o.value === savedCat)) {
      catEl.value = savedCat;
    }

    // map to track previous selections per category so we can detect newly-added selections
    const prevSelections = {};

    function populateSourcesForCategory() {
      const cat = catEl.value;
      const list = Object.keys(sources[cat] || {});
      srcEl.innerHTML = '';
      // load saved selections fresh for this category (fallback to legacy key)
      let savedSelectedNow = [];
      try {
        savedSelectedNow = JSON.parse(localStorage.getItem(STORAGE_SELECTED + '_' + cat) || localStorage.getItem(STORAGE_SELECTED) || '[]');
      } catch (e) {
        savedSelectedNow = [];
      }
      const savedLooksNumeric = savedSelectedNow.length && savedSelectedNow.every(x => String(x).match(/^\d+$/));
      for (let idx = 0; idx < list.length; idx++) {
        const s = list[idx];
        const o = document.createElement('option');
        o.value = s;
        o.textContent = s;
        if (savedLooksNumeric) {
          if (savedSelectedNow.includes(String(idx))) o.selected = true;
        } else {
          if (savedSelectedNow.includes(s)) o.selected = true;
        }
        srcEl.appendChild(o);
      }
      const currentSelected = Array.from(srcEl.selectedOptions).map(o => o.value);
      localStorage.setItem(STORAGE_SELECTED + '_' + cat, JSON.stringify(currentSelected));
      prevSelections[cat] = currentSelected.slice();
    }

    // when category changes, persist and repopulate
    catEl.addEventListener('change', () => {
      localStorage.setItem(STORAGE_CAT, catEl.value);
      populateSourcesForCategory();
    });

    // when selection changes, persist per-category
    srcEl.addEventListener('change', () => {
      const cat = catEl.value;
      const sel = Array.from(srcEl.selectedOptions).map(o => o.value);
      // persist
      localStorage.setItem(STORAGE_SELECTED + '_' + cat, JSON.stringify(sel));
      // find newly added selections and open them immediately
      const prev = prevSelections[cat] || [];
      const added = sel.filter(s => !prev.includes(s));
      if (added.length) {
        try {
          const q = document.getElementById('q').value.trim() || '';
          const urls = added.map(s => {
            const template = (sources[cat] || {})[s];
            if (!template) return null;
            return template.replace('{query}', encodeURIComponent(q));
          }).filter(Boolean);
          const tabs = [];
          for (let i = 0; i < urls.length; i++) tabs.push(window.open('about:blank', '_blank', 'noopener'));
          for (let i = 0; i < urls.length; i++) {
            const tab = tabs[i];
            const url = urls[i];
            try {
              if (tab) tab.location = url; else window.open(url, '_blank', 'noopener');
            } catch (e) {
              if (tab) tab.close();
              window.open(url, '_blank', 'noopener');
            }
          }
        } catch (e) {
          console.error('Error opening newly selected sources', e);
        }
      }
      prevSelections[cat] = sel.slice();
    });

    // select all button
    const selectAllBtn = document.getElementById('selectAllBtn');
    if (selectAllBtn) {
      selectAllBtn.addEventListener('click', () => {
        for (const opt of Array.from(srcEl.options)) opt.selected = true;
        const sel = Array.from(srcEl.selectedOptions).map(o => o.value);
        localStorage.setItem(STORAGE_SELECTED + '_' + catEl.value, JSON.stringify(sel));
      });
    }

    populateSourcesForCategory();

    document.getElementById('openSourceBtn').addEventListener('click', async () => {
      const category = catEl.value;
      const q = document.getElementById('q').value.trim() || '';
      const selected = Array.from(srcEl.selectedOptions).map(o => o.value);
      if (!selected.length) {
        alert('Please select one or more sources.');
        return;
      }
      try {
        // build URLs synchronously from the templates returned in `sources`
        const urls = selected.map(s => {
          const template = (sources[category] || {})[s];
          if (!template) return null;
          return template.replace('{query}', encodeURIComponent(q));
        }).filter(Boolean);

        console.log('Opening URLs for selected sources:', selected, urls);

        if (!urls.length) {
          alert('No URLs could be constructed for the selected sources.');
          return;
        }

        // Open placeholder tabs synchronously to avoid popup blocking, then set their locations
        const tabs = [];
        for (let i = 0; i < urls.length; i++) {
          const t = window.open('about:blank', '_blank', 'noopener');
          tabs.push(t);
        }
        for (let i = 0; i < urls.length; i++) {
          const url = urls[i];
          const tab = tabs[i];
          try {
            if (tab) tab.location = url; else window.open(url, '_blank', 'noopener');
          } catch (e) {
            if (tab) tab.close();
            window.open(url, '_blank', 'noopener');
          }
        }
      } catch (e) {
        console.error('Error opening source searches', e);
        alert('Could not open one or more source searches');
      }
    });

    // Open selected sources in the Link Hub (reliable fallback for popup-blocking)
    document.getElementById('openSourceHubBtn').addEventListener('click', () => {
      const category = catEl.value;
      const q = document.getElementById('q').value.trim() || '';
      const selected = Array.from(srcEl.selectedOptions).map(o => o.value);
      if (!selected.length) {
        alert('Please select one or more sources.');
        return;
      }
      const urls = selected.map(s => {
        const template = (sources[category] || {})[s];
        if (!template) return null;
        return template.replace('{query}', encodeURIComponent(q));
      }).filter(Boolean);
      if (!urls.length) {
        alert('No URLs could be constructed for the selected sources.');
        return;
      }
      // encode as fragment so server isn't involved; link_hub.html reads the fragment
      const payload = encodeURIComponent(JSON.stringify(urls));
      const hub = window.open('/static/link_hub.html#' + payload, '_blank');
      if (!hub) {
        // final fallback: open hub in same tab
        window.location.href = '/static/link_hub.html#' + payload;
      }
    });

    // open selected sources immediately on double-click (convenience)
    srcEl.addEventListener('dblclick', () => {
      const category = catEl.value;
      const q = document.getElementById('q').value.trim() || '';
      const selected = Array.from(srcEl.selectedOptions).map(o => o.value);
      if (!selected.length) return;
      try {
        const urls = selected.map(s => {
          const template = (sources[category] || {})[s];
          if (!template) return null;
          return template.replace('{query}', encodeURIComponent(q));
        }).filter(Boolean);

        // open synchronously using placeholder tabs to avoid popup blocking
        const tabs = [];
        for (let i = 0; i < urls.length; i++) tabs.push(window.open('about:blank', '_blank', 'noopener'));
        for (let i = 0; i < urls.length; i++) {
          const tab = tabs[i];
          const url = urls[i];
          try {
            if (tab) tab.location = url; else window.open(url, '_blank', 'noopener');
          } catch (e) {
            if (tab) tab.close();
            window.open(url, '_blank', 'noopener');
          }
        }
      } catch (e) {
        console.error('Error opening on double-click', e);
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
