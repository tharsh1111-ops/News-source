from typing import Dict, Any

NEWS_SOURCES: Dict[str, Dict[str, str]] = {
    "Global Agencies": {
        "Reuters": "https://www.reuters.com/site-search/?query={query}",
        "Associated Press": "https://apnews.com/search?q={query}",
        "AFP": "https://www.afp.com/en/search/site/{query}",
        "Xinhua": "https://search.news.cn/?lang=en&q={query}",
        "Anadolu Agency": "https://www.aa.com.tr/en/search?searchText={query}",
        "TASS": "https://tass.com/search?q={query}",
        "Kyodo News": "https://english.kyodonews.net/search.html?keyword={query}",
        "DPA": "https://www.dpa-international.com/search?q={query}",
        "PTI": "https://www.ptinews.com/search.aspx?query={query}",
    },
    "United States": {
        "CNN": "https://www.cnn.com/search?q={query}",
        "ABC News": "https://abcnews.go.com/search?searchtext={query}",
        "NPR": "https://www.npr.org/search?query={query}",
        "USA Today": "https://www.usatoday.com/search/?q={query}",
        "The New York Times": "https://www.nytimes.com/search/?query={query}",
        "The Washington Post": "https://www.washingtonpost.com/newssearch/?query={query}",
        "Los Angeles Times": "https://www.latimes.com/search?q={query}",
        "Chicago Tribune": "https://www.chicagotribune.com/search/?q={query}",
        "The Wall Street Journal": "https://www.wsj.com/search?query={query}",
        "The Atlantic": "https://www.theatlantic.com/search/?q={query}",
        "Vox": "https://www.vox.com/search?q={query}",
        "FiveThirtyEight": "https://fivethirtyeight.com/search/?q={query}",
        "ProPublica": "https://www.propublica.org/search?q={query}",
        "The Hill": "https://thehill.com/search/?q={query}",
        "Axios": "https://www.axios.com/search?q={query}",
        "Newsweek": "https://www.newsweek.com/search/site/{query}",
        "Time": "https://time.com/search/?q={query}",
        "The New Yorker": "https://www.newyorker.com/search/q/{query}",
        "The Intercept": "https://theintercept.com/search/?q={query}",
        "Mother Jones": "https://www.motherjones.com/search/?q={query}",
        "The Daily Beast": "https://www.thedailybeast.com/search?q={query}",
        "Business Insider": "https://www.businessinsider.com/s?q={query}",
        "MarketWatch": "https://www.marketwatch.com/search?q={query}",
        "The Verge": "https://www.theverge.com/search?q={query}",
        "Wired": "https://www.wired.com/search/?q={query}",
        "Politifact": "https://www.politifact.com/search/?q={query}",
        "Snopes": "https://www.snopes.com/search/?q={query}",
    },
    "United Kingdom": {
        "BBC": "https://www.bbc.co.uk/search?q={query}",
        "Sky News": "https://news.sky.com/search?q={query}",
        "ITV News": "https://www.itv.com/news/search?q={query}",
        "The Guardian": "https://www.theguardian.com/search?q={query}",
        "The Times": "https://www.thetimes.co.uk/search?q={query}",
        "The Telegraph": "https://www.telegraph.co.uk/search.html?queryText={query}",
        "The Independent": "https://www.independent.co.uk/search?q={query}",
        "Financial Times": "https://www.ft.com/search?q={query}",
        "The Economist": "https://www.economist.com/search?q={query}",
        "Daily Mail": "https://www.dailymail.co.uk/home/search.html?searchPhrase={query}",
    },
    "Europe": {
        "Der Spiegel": "https://www.spiegel.de/suche/?suchbegriff={query}",
        "Die Welt": "https://www.welt.de/suche/?query={query}",
        "Le Monde": "https://www.lemonde.fr/recherche/?search_keywords={query}",
        "Le Figaro": "https://recherche.lefigaro.fr/recherche/{query}",
        "El País": "https://elpais.com/buscador/?q={query}",
        "La Repubblica": "https://www.repubblica.it/ricerca/?query={query}",
        "Corriere della Sera": "https://www.corriere.it/ricerca/?query={query}",
        "NOS": "https://nos.nl/zoeken?q={query}",
        "NRC": "https://www.nrc.nl/zoeken/?q={query}",
        "Politico Europe": "https://www.politico.eu/?s={query}",
    },
    "Canada": {
        "CBC": "https://www.cbc.ca/search?q={query}",
        "CTV News": "https://www.ctvnews.ca/search-results/search-ctv-news-7.137?q={query}",
        "Global News": "https://globalnews.ca/?s={query}",
        "Toronto Star": "https://www.thestar.com/search.html?q={query}",
        "National Post": "https://nationalpost.com/search/?q={query}",
    },
    "Australia": {
        "ABC News Australia": "https://www.abc.net.au/news/search/?q={query}",
        "SBS News": "https://www.sbs.com.au/news/search/{query}",
        "The Sydney Morning Herald": "https://www.smh.com.au/search?text={query}",
        "The Age": "https://www.theage.com.au/search?text={query}",
        "News.com.au": "https://www.news.com.au/search-results?q={query}",
    },
    "India": {
        "The Hindu": "https://www.thehindu.com/search/?q={query}",
        "Times of India": "https://timesofindia.indiatimes.com/topic/{query}",
        "Hindustan Times": "https://www.hindustantimes.com/search?q={query}",
        "NDTV": "https://www.ndtv.com/search?searchtext={query}",
        "India Today": "https://www.indiatoday.in/topic/{query}",
        "The Indian Express": "https://indianexpress.com/?s={query}",
    },
    "Japan": {
        "NHK": "https://www3.nhk.or.jp/nhkworld/en/search/?q={query}",
        "Asahi Shimbun": "https://www.asahi.com/english/search/?q={query}",
        "Yomiuri Shimbun": "https://www.yomiuri.co.jp/search/?q={query}",
        "Nikkei Asia": "https://asia.nikkei.com/search?q={query}",
    },
    "South Korea": {
        "Yonhap News": "https://en.yna.co.kr/search/index?query={query}",
        "The Korea Herald": "http://www.koreaherald.com/search/index.php?query={query}",
        "The Korea Times": "https://www.koreatimes.co.kr/www2/common/search.asp?kwd={query}",
    },
    "China": {
        "China Daily": "https://www.chinadaily.com.cn/search?query={query}",
        "Global Times": "https://www.globaltimes.cn/search?keyword={query}",
        "South China Morning Post": "https://www.scmp.com/search/{query}",
    },
    "Middle East": {
        "Al Jazeera": "https://www.aljazeera.com/Search/?q={query}",
        "Al Arabiya": "https://english.alarabiya.net/tools/search?query={query}",
        "Gulf News": "https://gulfnews.com/search?q={query}",
        "The National (UAE)": "https://www.thenationalnews.com/search?q={query}",
        "Haaretz": "https://www.haaretz.com/search?q={query}",
        "Jerusalem Post": "https://www.jpost.com/search?q={query}",
    },
    "Africa": {
        "AllAfrica": "https://allafrica.com/search/?search_string={query}",
        "Daily Nation": "https://nation.africa/search?q={query}",
        "Mail & Guardian": "https://mg.co.za/search/?q={query}",
        "The Guardian Nigeria": "https://guardian.ng/?s={query}",
    },
    "Latin America": {
        "Folha de S.Paulo": "https://search.folha.uol.com.br/?q={query}",
        "O Globo": "https://oglobo.globo.com/busca/?q={query}",
        "Clarín": "https://www.clarin.com/tema/{query}.html",
        "El Universal (Mexico)": "https://www.eluniversal.com.mx/buscador?search_api_fulltext={query}",
        "La Nación (Argentina)": "https://www.lanacion.com.ar/buscar/?query={query}",
    },
}


def list_sources() -> Dict[str, Any]:
    """Return the available categories and sources (names only)."""
    return {cat: list(sources.keys()) for cat, sources in NEWS_SOURCES.items()}


def list_sources_full() -> Dict[str, Dict[str, str]]:
    """Return the full mapping of categories -> {source: url_template}.

    Useful for clients that want to format URLs locally to avoid extra server round-trips.
    """
    return NEWS_SOURCES


def get_search_url(category: str, source: str, query: str) -> str:
    """Return a formatted search URL for the given source and query.

    Raises KeyError if category/source not found.
    """
    cat = NEWS_SOURCES.get(category)
    if not cat:
        raise KeyError(f"Unknown category: {category}")
    template = cat.get(source)
    if not template:
        raise KeyError(f"Unknown source: {source} in category {category}")
    return template.format(query=query)
