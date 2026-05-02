import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import io
import time
import json
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="Amity Research Intelligence",
    layout="wide",
    page_icon="🎓",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────
# PROFESSIONAL CSS THEME
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    color: #ffffff;
}

.main .block-container {
    padding: 2rem 3rem;
    max-width: 1400px;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    border-right: 1px solid rgba(255,255,255,0.1);
}

[data-testid="stSidebar"] * {
    color: #e0e0ff !important;
}

[data-testid="metric-container"] {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 16px;
    padding: 1.2rem 1rem;
    backdrop-filter: blur(10px);
    transition: transform 0.2s;
}

[data-testid="metric-container"]:hover {
    transform: translateY(-4px);
    border-color: rgba(99,179,237,0.5);
}

[data-testid="stMetricValue"] {
    color: #63b3ed !important;
    font-weight: 700 !important;
    font-size: 2rem !important;
}

[data-testid="stMetricLabel"] {
    color: #a0aec0 !important;
    font-size: 0.85rem !important;
}

.streamlit-expanderHeader {
    background: rgba(255,255,255,0.05) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: #ffffff !important;
    font-weight: 600 !important;
}

.streamlit-expanderContent {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 0 0 12px 12px !important;
}

.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white !important;
    border: none;
    border-radius: 25px;
    padding: 0.6rem 2rem;
    font-weight: 600;
    font-size: 0.95rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(102,126,234,0.4);
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102,126,234,0.6);
}

.stTextInput > div > div > input {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 12px !important;
    color: white !important;
    padding: 0.8rem 1rem !important;
}

.stTextInput > div > div > input:focus {
    border-color: #667eea !important;
    box-shadow: 0 0 0 2px rgba(102,126,234,0.3) !important;
}

.stSelectbox > div > div {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 12px !important;
    color: white !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.05);
    border-radius: 12px;
    padding: 4px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    color: #a0aec0;
    font-weight: 500;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: white !important;
}

hr {
    border-color: rgba(255,255,255,0.1) !important;
}

.stSuccess {
    background: rgba(72,187,120,0.15) !important;
    border-color: #48bb78 !important;
    border-radius: 10px !important;
}

.stError {
    background: rgba(252,129,74,0.15) !important;
    border-color: #fc814a !important;
    border-radius: 10px !important;
}

.stInfo {
    background: rgba(99,179,237,0.12) !important;
    border-color: #63b3ed !important;
    border-radius: 10px !important;
}

.stWarning {
    background: rgba(246,173,85,0.15) !important;
    border-color: #f6ad55 !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# GLOBAL CONFIG
# ─────────────────────────────────────────────────────────────
IEEE_API_KEY = ""

PLATFORM_COLORS = {
    'Google Scholar': '#4285F4',
    'ResearchGate': '#00CCBB',
    'IEEE Xplore': '#00629B',
    'Scopus': '#FF6B35',
    'ORCID': '#A6CE39',
    'None': '#555555',
    'Other': '#888888'
}

PLATFORM_ICONS = {
    'Google Scholar': '🎓',
    'ResearchGate': '🧪',
    'IEEE Xplore': '⚡',
    'Scopus': '🔬',
    'ORCID': '🌿',
    'None': '—',
    'Other': '🔗'
}

PLATFORM_GRADIENT = {
    'Google Scholar': 'linear-gradient(135deg,#4285F4,#34A853)',
    'ResearchGate': 'linear-gradient(135deg,#00CCBB,#009688)',
    'IEEE Xplore': 'linear-gradient(135deg,#00629B,#004f80)',
    'Scopus': 'linear-gradient(135deg,#FF6B35,#e05320)',
    'ORCID': 'linear-gradient(135deg,#A6CE39,#7cb518)',
    'None': 'linear-gradient(135deg,#555,#333)',
    'Other': 'linear-gradient(135deg,#888,#555)'
}

CHART_THEME = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(255,255,255,0.03)',
    font=dict(family='Inter', color='#e0e0ff', size=13),
    margin=dict(l=40, r=40, t=60, b=40)
)

# ─────────────────────────────────────────────────────────────
# LOAD CSV
# ─────────────────────────────────────────────────────────────
@st.cache_data
def load_faculty_data():
    csv_data = """Sr No,Faculty Name,School,Profile Link
1,Dr. Ajay Rana (DG Sir),ASET,
2,Abha Shree Pandey,AISS,
3,Abhishek Kumar (ME),ASET,
4,Abhishek Sharma (Pharmacy),ASP,
5,Aditi Dhama,ASFT,
6,Aizad Khursheed,ASET,
7,Akanksha Singh (BJMC),ASET,
8,Akanksha Singh (ECE),ASET,
9,Amardeep Gupta,ASET,
10,Amitabh Bhargava,ABS,
11,Ankesh Kumar,AIAS,
12,Ankita Mathur,AIAS,
13,Anmol Tiwari,AIPS,
14,Anshika Nautiyal,ABS,
15,Anshita Thakur,ASFT,
16,Ashish Kumar Yadav,ASET,
17,Atul Kumar,A. Polytechnic,https://ieeexplore.ieee.org/author/37085542563
18,Ayushi Thakur,ASET,
19,Bhanu Prakash Lohani,ASET,https://ieeexplore.ieee.org/author/37089487585
20,Deepshikha Bhargava,ASET,
21,Desh Pal Singh,AIAS,https://www.researchgate.net/profile/Dhirendra-Patel-3/research
22,Dhirendra Patel,ASET,https://www.researchgate.net/profile/Dhirendra-Patel-3/research
23,Diksha Panwar,ABS,
24,Divya Singh,ASET,
25,Durgesh Kumar Jha,ASET,
26,Dweep Chand Singh,AIBHAS,
27,Garima Bhardwaj,ABS,
28,Garima Panwar,ASET,
29,Gaurav Gupta,ABS,
30,Gaurav Mishra,AIAS,
31,Gaurav Panwar,ASET,
32,Gourav Tomar,ASET,
33,Girish Kumar,ASP,
34,Girish Paliwal,ASET,
35,Gulshan Kumar,AISS,
36,Gurmeet Kaur,AISS,
37,Himansu Kumar Srivastwa,AIBHAS,
38,Ishu Chaudhary,ASET,
39,Janki Kumari,Allied Sciences,
40,Kanta Prasad Sharma,ASET,
41,Kirti Dilip Singh,ASET,
42,Krashn Kant Gupta,Polytechnic,
43,Lipsa Das,ASET,
44,Manish Kumar,AIP,
45,Manjeet Singh,ASET,
46,Meenakshi,ASET,
47,Melita Stephen,ABS,
48,Murari Lal Azad,ASET,https://scholar.google.com/citations?user=aJV0ktoAAAAJ&hl=en
49,Nandita Tripathi,AIPS,
50,Neeraj Kumar Chouhan,ASP,
51,Neha Tyagi,ASET,
52,Palak Vishnoi,ASFT,
53,Pooja Anand,ASET,
54,Pooja Singh,ACCF,
55,Pradeep Kr. Kushwaha,ASET,
56,Pramit Kumar Samant,ASET,
57,Prateek Chaturvedi,ASET,
58,Preeti Singh Bahadur,AIAS,
59,Priyanka Kumari,AIBHAS,
60,Rajeev Kumar Rai,,
61,Rajeev Semwal,AIPS,
62,Riya Chauhan,AIPS,
63,Ruchira Srivastava,ASET,
64,S Vikram Singh,ASET,
65,Sailaja Bohara,ABS,
66,Samridhi Dev,ASET,
67,Dr. Sandeep Mathur,ASET,
68,Shakeeluddin,AIAS,
69,Shalini Jaiswal,AIAS,
70,Shalini Srivastav,ACCF,
71,Shiv Ranjan,ASB,
72,Shivendra Singh Chaudhary,ABS,
73,Shobhit Mishra,Polytecnic,
74,Shubhi Gupta,ASET,
75,Siddhartha Saini,AIIT,
76,Sonam Rani,ACCF,
77,Sonia Tyagi,AIESR,
78,Subhadra Rajpoot,AIAS,
79,Subodh Barthwal,ASET,
80,Sunaina Chaudhary,AIAS,
81,Tanisha Agarwal,AIPS,
82,Tanya Gupta,ASET,
83,Tarun Virmani,AIP,
84,Vernika Misra,ACCF,
85,Vijay,ASET,
86,Yukti Sharma,AIPS,
87,Tejaswi Khanna,ASET,"""
    df = pd.read_csv(io.StringIO(csv_data))
    df['Profile Link'] = df['Profile Link'].fillna('').str.strip()
    df['Has_Profile']  = df['Profile Link'] != ''
    df['Platform']     = df['Profile Link'].apply(detect_platform)
    return df


def detect_platform(url):
    if not url: return 'None'
    u = url.lower()
    if 'scopus.com'       in u: return 'Scopus'
    if 'scholar.google'   in u: return 'Google Scholar'
    if 'researchgate.net' in u: return 'ResearchGate'
    if 'ieeexplore.ieee'  in u: return 'IEEE Xplore'
    if 'orcid.org'        in u: return 'ORCID'
    return 'Other'


# ─────────────────────────────────────────────────────────────
# FETCHERS
# ─────────────────────────────────────────────────────────────
def get_base_headers(idx=0):
    agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36',
    ]
    return {
        'User-Agent':      agents[idx % len(agents)],
        'Accept':          'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection':      'keep-alive',
    }


# ── Google Scholar ───────────────────────────────────────────
def fetch_google_scholar(url):
    try:
        from scholarly import scholarly as sc
        user_match = re.search(r'user=([\w-]+)', url)
        if not user_match:
            return {'status': 'error', 'message': 'Invalid Google Scholar URL'}
        author = sc.search_author_id(user_match.group(1))
        author = sc.fill(author, sections=['basics', 'indices', 'counts', 'publications'])
        pubs   = author.get('publications', [])
        pub_records = []
        for p in pubs[:10]:
            bib = p.get('bib', {})
            pub_records.append({
                'title':    bib.get('title', 'N/A'),
                'year':     bib.get('pub_year', 'N/A'),
                'venue':    bib.get('citation', 'N/A')[:80],
                'cited_by': p.get('num_citations', 0)
            })
        return {
            'status':            'success',
            'source':            'Google Scholar (scholarly) ✅',
            'platform':          'Google Scholar',
            'name':              author.get('name', 'N/A'),
            'affiliation':       author.get('affiliation', 'N/A'),
            'email_domain':      author.get('email_domain', ''),
            'interests':         author.get('interests', []),
            'documents':         len(pubs),
            'citations':         author.get('citedby', 0),
            'citations5y':       author.get('citedby5y', 0),
            'i10_index':         author.get('i10index', 0),
            'i10_index5y':       author.get('i10index5y', 0),
            'citations_per_doc': round(author.get('citedby', 0) / max(len(pubs), 1), 2),
            'citation_by_year':  author.get('cites_per_year', {}),
            'pub_records':       pub_records,
            'profile_url':       url
        }
    except Exception as e:
        return {'status': 'error', 'message': f'scholarly: {str(e)[:150]}'}


# ── ResearchGate ─────────────────────────────────────────────
def fetch_researchgate(url):
    try:
        from playwright.sync_api import sync_playwright
        profile_url = re.sub(r'/research.*$', '', url)
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
            ctx = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36',
                viewport={'width': 1440, 'height': 900}, locale='en-US')
            page = ctx.new_page()
            page.route("**/*.{png,jpg,jpeg,gif,svg,woff,woff2,mp4,webp}", lambda r: r.abort())
            page.goto(profile_url, wait_until='domcontentloaded', timeout=35000)
            time.sleep(3)
            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text(' ', strip=True)

            name_tag    = soup.find('h1') or soup.find('span', {'itemprop': 'name'})
            name        = name_tag.get_text(strip=True) if name_tag else 'N/A'
            inst_tag    = soup.find('div', class_=re.compile(r'institution|department', re.I))
            affiliation = inst_tag.get_text(strip=True)[:120] if inst_tag else 'N/A'

            ri_m    = re.search(r'([\d,]+)\s*Research\s*[Ii]tem', text)
            cit_m   = re.search(r'([\d,]+)\s*[Cc]itation', text)
            rd_m    = re.search(r'([\d,]+)\s*[Rr]ead', text)
            rec_m   = re.search(r'([\d,]+)\s*[Rr]ecommendation', text)
            fol_m   = re.search(r'([\d,]+)\s*[Ff]ollower', text)
            score_m = re.search(r'RG\s*[Ss]core[:\s]*([\d.]+)', text)

            documents       = int(ri_m.group(1).replace(',',''))   if ri_m    else 0
            citations       = int(cit_m.group(1).replace(',',''))  if cit_m   else 0
            reads           = int(rd_m.group(1).replace(',',''))   if rd_m    else 0
            recommendations = int(rec_m.group(1).replace(',',''))  if rec_m   else 0
            followers       = int(fol_m.group(1).replace(',',''))  if fol_m   else 0
            rg_score        = float(score_m.group(1))              if score_m else 0.0

            tags      = [t.get_text(strip=True) for t in
                         soup.find_all('a', href=re.compile(r'/topic/'))
                         if t.get_text(strip=True)][:8]
            coauthors = [c.get_text(strip=True) for c in
                         soup.find_all('a', href=re.compile(r'/profile/'))
                         if len(c.get_text(strip=True)) > 3][:6]
            pub_records = []
            for h in soup.find_all(['h3','h4'], limit=30):
                t = h.get_text(strip=True)
                if 20 < len(t) < 200:
                    pub_records.append({'title': t, 'year':'N/A','venue':'N/A','cited_by':0})
            browser.close()
            return {
                'status':          'success',
                'source':          'ResearchGate (Playwright) ✅',
                'platform':        'ResearchGate',
                'name':            name,
                'affiliation':     affiliation,
                'documents':       documents,
                'citations':       citations,
                'reads':           reads,
                'recommendations': recommendations,
                'followers':       followers,
                'rg_score':        rg_score,
                'interests':       tags,
                'coauthors':       coauthors,
                'citations_per_doc': round(citations / max(documents, 1), 2),
                'pub_records':     pub_records[:8],
                'profile_url':     profile_url
            }
    except Exception as e:
        return {'status': 'error', 'message': f'Playwright RG: {str(e)[:150]}'}


# ── IEEE Xplore — 5-Layer Fallback ───────────────────────────
def fetch_ieee(url):
    try:
        ieee_id = re.search(r'/author/(\d+)', url)
        if not ieee_id:
            return {'status': 'error', 'message': 'Invalid IEEE URL'}

        author_id    = ieee_id.group(1)
        base_headers = {
            'User-Agent':       'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0 Safari/537.36',
            'Referer':          'https://ieeexplore.ieee.org/',
            'Accept':           'application/json, text/html, */*',
            'Accept-Language':  'en-US,en;q=0.9',
            'X-Requested-With': 'XMLHttpRequest',
        }

        def build_result(source, name, affiliation, total, citations,
                         year_counts, content_types, pub_records, note=''):
            return {
                'status':            'success',
                'source':            source,
                'platform':          'IEEE Xplore',
                'name':              name,
                'affiliation':       affiliation,
                'documents':         total,
                'citations':         citations,
                'citations_per_doc': round(citations / max(total, 1), 2),
                'year_counts':       year_counts,
                'content_types':     content_types,
                'pub_records':       pub_records,
                'profile_url':       url,
                '_note':             note
            }

        def parse_records(records, aid):
            citations = sum(int(r.get('citationCount', 0) or 0) for r in records)
            name, affiliation = 'N/A', 'N/A'
            for rec in records[:5]:
                for auth in rec.get('authors', []):
                    if str(auth.get('id', '')) == aid:
                        name        = auth.get('preferredName', auth.get('fullName', 'N/A'))
                        affiliation = auth.get('affiliation', 'N/A')
                        break
                if name != 'N/A': break
            year_counts, content_types, pub_records = {}, {}, []
            for rec in records:
                yr = str(rec.get('publicationYear', ''))
                if yr: year_counts[yr] = year_counts.get(yr, 0) + 1
                ct = rec.get('contentType', 'Unknown')
                content_types[ct] = content_types.get(ct, 0) + 1
            for rec in sorted(records,
                               key=lambda x: int(x.get('citationCount', 0) or 0),
                               reverse=True)[:8]:
                pub_records.append({
                    'title':    rec.get('title', 'N/A'),
                    'year':     rec.get('publicationYear', 'N/A'),
                    'venue':    rec.get('publicationTitle', 'N/A')[:80],
                    'cited_by': int(rec.get('citationCount', 0) or 0)
                })
            return name, affiliation, citations, year_counts, content_types, pub_records

        # ══ LAYER 1 — Official IEEE API ══════════════════════
        if IEEE_API_KEY.strip():
            try:
                api_url = (
                    f"https://ieeexploreapi.ieee.org/api/v1/search/articles"
                    f"?apikey={IEEE_API_KEY}&author_id={author_id}"
                    f"&max_records=25&sort_order=desc&sort_field=citation_count&format=json"
                )
                r = requests.get(api_url, headers=base_headers, timeout=15)
                if r.status_code == 200:
                    data      = r.json()
                    records   = data.get('articles', [])
                    total     = data.get('total_records', len(records))
                    citations = sum(int(rec.get('citing_paper_count', 0) or 0) for rec in records)
                    name, affiliation = 'N/A', 'N/A'
                    for rec in records[:5]:
                        for auth in rec.get('authors', {}).get('authors', []):
                            if str(auth.get('author_id', '')) == author_id:
                                name        = auth.get('full_name', 'N/A')
                                affiliation = auth.get('affiliation', 'N/A')
                                break
                        if name != 'N/A': break
                    year_counts, content_types, pub_records = {}, {}, []
                    for rec in records:
                        yr = str(rec.get('publication_year', ''))
                        if yr: year_counts[yr] = year_counts.get(yr, 0) + 1
                        ct = rec.get('content_type', 'Unknown')
                        content_types[ct] = content_types.get(ct, 0) + 1
                    for rec in sorted(records,
                                      key=lambda x: int(x.get('citing_paper_count', 0) or 0),
                                      reverse=True)[:8]:
                        pub_records.append({
                            'title':    rec.get('title', 'N/A'),
                            'year':     rec.get('publication_year', 'N/A'),
                            'venue':    rec.get('publication_title', 'N/A')[:80],
                            'cited_by': int(rec.get('citing_paper_count', 0) or 0)
                        })
                    return build_result('IEEE Official API ✅', name, affiliation,
                                        total, citations, year_counts, content_types, pub_records)
            except Exception:
                pass

        # ══ LAYER 2 — IEEE Internal REST ═════════════════════
        try:
            endpoints = [
                f"https://ieeexplore.ieee.org/rest/author/{author_id}",
                (f"https://ieeexplore.ieee.org/rest/search?newsearch=true"
                 f"&author_ids={author_id}&rowsPerPage=25&pageNumber=1"
                 f"&sortType=paper_citation_count_desc"),
                (f"https://ieeexplore.ieee.org/rest/search?newsearch=true"
                 f"&queryText=&author={author_id}"
                 f"&pageNumber=1&rowsPerPage=25&sortType=paper_citation_count_desc"),
            ]
            for ep in endpoints:
                try:
                    r = requests.get(ep, headers=base_headers, timeout=10)
                    if r.status_code == 200:
                        data = r.json()
                        if 'articleCount' in data or 'firstName' in data:
                            name = f"{data.get('firstName','')} {data.get('lastName','')}".strip() or 'N/A'
                            aff  = data.get('institution', data.get('affiliation', 'N/A'))
                            tot  = data.get('articleCount', 0)
                            cit  = data.get('citationCount', 0)
                            return build_result('IEEE Internal API ✅', name, aff, tot, cit, {}, {}, [])
                        records = data.get('records', [])
                        if records:
                            total  = data.get('totalRecords', len(records))
                            nm, af, ci, yc, ct, pr = parse_records(records, author_id)
                            return build_result('IEEE Internal Search ✅', nm, af, total, ci, yc, ct, pr)
                except Exception:
                    continue
        except Exception:
            pass

        # ══ LAYER 3 — Selenium Stealth ═══════════════════════
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from webdriver_manager.chrome import ChromeDriverManager

            opts = Options()
            opts.add_argument("--headless=new")
            opts.add_argument("--no-sandbox")
            opts.add_argument("--disable-dev-shm-usage")
            opts.add_argument("--disable-blink-features=AutomationControlled")
            opts.add_argument("--window-size=1440,900")
            opts.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36")
            opts.add_experimental_option("excludeSwitches", ["enable-automation"])
            opts.add_experimental_option("useAutomationExtension", False)

            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()), options=opts)
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": "Object.defineProperty(navigator,'webdriver',{get:()=>undefined})"
            })
            driver.get(url)
            time.sleep(6)

            page_src = driver.page_source
            soup     = BeautifulSoup(page_src, 'html.parser')
            text     = soup.get_text(' ', strip=True)

            try:
                name_el = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'h1, .author-name')))
                name = name_el.text.strip() or 'N/A'
            except Exception:
                nm_tag = soup.find('h1')
                name   = nm_tag.get_text(strip=True) if nm_tag else 'N/A'

            aff_tag     = soup.find('div', class_=re.compile(r'affil|institution', re.I))
            affiliation = aff_tag.get_text(strip=True)[:120] if aff_tag else 'N/A'
            doc_m       = re.search(r'(\d[\d,]*)\s*(?:[Pp]aper|[Dd]ocument|[Aa]rticle)', text)
            cit_m       = re.search(r'(\d[\d,]*)\s*[Cc]itation', text)
            total       = int(doc_m.group(1).replace(',','')) if doc_m else 0
            citations   = int(cit_m.group(1).replace(',','')) if cit_m else 0

            year_counts, content_types, pub_records = {}, {}, []
            for script in driver.find_elements(By.TAG_NAME, 'script'):
                sc = script.get_attribute('innerHTML') or ''
                if 'publicationYear' in sc or 'citationCount' in sc:
                    try:
                        jm = re.search(r'\{.*?"records".*?\}', sc, re.DOTALL)
                        if jm:
                            parsed  = json.loads(jm.group(0))
                            records = parsed.get('records', [])
                            if records:
                                if not total: total = parsed.get('totalRecords', len(records))
                                nm2, af2, ci2, yc, ct, pr = parse_records(records, author_id)
                                if not citations: citations = ci2
                                year_counts   = yc
                                content_types = ct
                                pub_records   = pr
                            break
                    except Exception:
                        continue
            driver.quit()
            return build_result('IEEE Selenium ✅', name, affiliation,
                                 total, citations, year_counts, content_types, pub_records)
        except Exception:
            pass

        # ══ LAYER 4 — Playwright Fallback ════════════════════
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox','--disable-dev-shm-usage',
                          '--disable-blink-features=AutomationControlled'])
                ctx  = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0 Safari/537.36',
                    viewport={'width':1440,'height':900}, locale='en-US')
                page = ctx.new_page()
                page.route("**/*.{png,jpg,jpeg,gif,svg,woff,woff2,mp4,webp}",
                            lambda r: r.abort())
                page.goto(url, wait_until='domcontentloaded', timeout=35000)
                time.sleep(5)
                html = page.content()
                soup = BeautifulSoup(html, 'html.parser')
                text = soup.get_text(' ', strip=True)
                nm_tag      = soup.find('h1')
                name        = nm_tag.get_text(strip=True) if nm_tag else 'N/A'
                aff_tag     = soup.find('div', class_=re.compile(r'affil|institution', re.I))
                affiliation = aff_tag.get_text(strip=True)[:120] if aff_tag else 'N/A'
                doc_m       = re.search(r'(\d[\d,]*)\s*(?:[Pp]aper|[Dd]ocument|[Aa]rticle)', text)
                cit_m       = re.search(r'(\d[\d,]*)\s*[Cc]itation', text)
                total       = int(doc_m.group(1).replace(',','')) if doc_m else 0
                citations   = int(cit_m.group(1).replace(',','')) if cit_m else 0
                year_counts, content_types, pub_records = {}, {}, []
                for script in soup.find_all('script'):
                    sc = script.string or ''
                    if 'publicationYear' in sc or 'citationCount' in sc:
                        try:
                            jm = re.search(r'\{.*?"records".*?\}', sc, re.DOTALL)
                            if jm:
                                parsed  = json.loads(jm.group(0))
                                records = parsed.get('records', [])
                                if records:
                                    _, _, ci2, yc, ct, pr = parse_records(records, author_id)
                                    if not citations: citations = ci2
                                    year_counts   = yc
                                    content_types = ct
                                    pub_records   = pr
                                break
                        except Exception:
                            continue
                browser.close()
                return build_result('IEEE Playwright ✅', name, affiliation,
                                     total, citations, year_counts, content_types, pub_records)
        except Exception:
            pass

        # ══ LAYER 5 — Manual Entry Fallback ══════════════════
        return {
            'status':      'manual_required',
            'platform':    'IEEE Xplore',
            'profile_url': url,
            'author_id':   author_id,
            '_note':       (
                'All automated layers were blocked by IEEE. '
                'Enter data manually below OR get a free API key from '
                'https://developer.ieee.org/member/register'
            )
        }

    except Exception as e:
        return {'status': 'error', 'message': f'IEEE fetch failed: {str(e)[:150]}'}


# ── Scopus ───────────────────────────────────────────────────
def fetch_scopus(url):
    try:
        aid = re.search(r'authorId=([\w]+)', url)
        if not aid:
            return {'status': 'error', 'message': 'Invalid Scopus URL'}
        clean_url = f"https://www.scopus.com/authid/detail.uri?authorId={aid.group(1)}"
        r    = requests.get(clean_url, headers=get_base_headers(), timeout=12)
        text = r.text
        doc_m = re.search(r'(\d[\d,]*)\s*[Dd]ocument', text)
        cit_m = re.search(r'(\d[\d,]*)\s*[Cc]itation', text)
        return {
            'status':            'success',
            'source':            'Scopus ✅',
            'platform':          'Scopus',
            'name':              'See Profile',
            'affiliation':       'Amity University',
            'documents':         int(doc_m.group(1).replace(',','')) if doc_m else 0,
            'citations':         int(cit_m.group(1).replace(',','')) if cit_m else 0,
            'citations_per_doc': 0,
            'pub_records':       [],
            'profile_url':       clean_url
        }
    except Exception as e:
        return {'status': 'error', 'message': str(e)[:150]}


def fetch_author_data(url, platform):
    dispatch = {
        'Google Scholar': fetch_google_scholar,
        'ResearchGate':   fetch_researchgate,
        'IEEE Xplore':    fetch_ieee,
        'Scopus':         fetch_scopus,
    }
    fn = dispatch.get(platform)
    return fn(url) if fn else {'status': 'unsupported', 'message': f'{platform} not supported'}


# ─────────────────────────────────────────────────────────────
# CHART BUILDERS
# ─────────────────────────────────────────────────────────────
def apply_theme(fig):
    fig.update_layout(**CHART_THEME)
    fig.update_xaxes(gridcolor='rgba(255,255,255,0.08)', zerolinecolor='rgba(255,255,255,0.08)')
    fig.update_yaxes(gridcolor='rgba(255,255,255,0.08)', zerolinecolor='rgba(255,255,255,0.08)')
    return fig


def chart_bar_metrics(data, name, platform):
    mapping = [
        ('documents',       'Documents / Papers'),
        ('citations',       'Total Citations'),
        ('citations5y',     'Citations (5yr)'),
        ('i10_index',       'i10 Index'),
        ('i10_index5y',     'i10 Index (5yr)'),
        ('reads',           'Reads'),
        ('recommendations', 'Recommendations'),
        ('followers',       'Followers'),
        ('citations_per_doc','Citations / Doc'),
        ('rg_score',        'RG Score'),
    ]
    labels, values = [], []
    for k, l in mapping:
        v = data.get(k)
        if v is not None and v != 0:
            labels.append(l); values.append(v)
    if not labels: return None
    color = PLATFORM_COLORS.get(platform, '#667eea')
    fig = go.Figure(go.Bar(
        x=values, y=labels, orientation='h',
        marker=dict(color=list(range(len(labels))),
                    colorscale=[[0,'#667eea'],[0.5,color],[1,'#764ba2']],
                    line=dict(width=0)),
        text=[f"  {int(v):,}" if isinstance(v,(int,float)) and v>=1 else f"  {v}" for v in values],
        textposition='inside', insidetextanchor='start',
        textfont=dict(color='white', size=13)
    ))
    fig.update_layout(
        title=dict(text=f"📊 All Metrics — {name}", font=dict(size=16, color='#e0e0ff')),
        xaxis=dict(showticklabels=False),
        height=max(350, len(labels)*58), **CHART_THEME
    )
    fig.update_yaxes(gridcolor='rgba(0,0,0,0)')
    return fig


def chart_donut(data, name, platform):
    keys = [('documents','Documents'),('citations','Citations'),
            ('reads','Reads'),('recommendations','Recommendations'),('followers','Followers')]
    labels, values = [], []
    for k, l in keys:
        v = data.get(k, 0)
        if v and v > 0: labels.append(l); values.append(v)
    if not values: return None
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.55,
        marker=dict(colors=['#667eea','#764ba2','#00CCBB','#F6AD55','#FC8181']),
        textfont=dict(color='white', size=13), pull=[0.05]+[0]*(len(values)-1)
    ))
    fig.update_layout(
        title=dict(text="🍩 Metric Distribution", font=dict(size=16, color='#e0e0ff')),
        height=420, legend=dict(font=dict(color='#e0e0ff')), **CHART_THEME
    )
    return fig


def chart_yearly_citations(citation_by_year, name):
    if not citation_by_year: return None
    years  = sorted(citation_by_year.keys())
    counts = [citation_by_year[y] for y in years]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years, y=counts, mode='lines+markers', fill='tozeroy',
        line=dict(color='#667eea', width=3), fillcolor='rgba(102,126,234,0.2)',
        marker=dict(size=8, color='#764ba2', line=dict(color='white', width=2))
    ))
    fig.update_layout(
        title=dict(text="📅 Year-wise Citation Trend", font=dict(size=16, color='#e0e0ff')),
        xaxis_title='Year', yaxis_title='Citations', height=380, **CHART_THEME
    )
    return fig


def chart_yearly_pubs(year_counts, name):
    if not year_counts: return None
    years  = sorted(year_counts.keys())
    counts = [year_counts[y] for y in years]
    fig = go.Figure(go.Bar(
        x=years, y=counts,
        marker=dict(color=counts, colorscale='Purples', line=dict(width=0))
    ))
    fig.update_layout(
        title=dict(text="📅 Publications Per Year", font=dict(size=16, color='#e0e0ff')),
        xaxis_title='Year', yaxis_title='Papers', height=380, **CHART_THEME
    )
    return fig


def chart_content_types(content_types, name):
    if not content_types: return None
    fig = go.Figure(go.Pie(
        labels=list(content_types.keys()), values=list(content_types.values()),
        marker=dict(colors=['#667eea','#764ba2','#00CCBB','#F6AD55','#FC8181']),
        hole=0.4, textfont=dict(color='white')
    ))
    fig.update_layout(
        title=dict(text="📂 Content Types", font=dict(size=16, color='#e0e0ff')),
        height=380, legend=dict(font=dict(color='#e0e0ff')), **CHART_THEME
    )
    return fig


def chart_pub_citations(pub_records, name):
    if not pub_records: return None
    sp = sorted(pub_records, key=lambda x: x.get('cited_by',0), reverse=True)[:8]
    sp = [p for p in sp if p.get('title','N/A') != 'N/A']
    if not sp: return None
    titles   = [p['title'][:45]+'…' if len(p['title'])>45 else p['title'] for p in sp]
    cited_by = [p.get('cited_by', 0) for p in sp]
    fig = go.Figure(go.Bar(
        x=cited_by, y=titles, orientation='h',
        text=[f"{c:,} citations" for c in cited_by],
        textposition='outside', textfont=dict(color='#e0e0ff'),
        marker=dict(color=cited_by, colorscale=[[0,'#667eea'],[1,'#764ba2']],
                    line=dict(width=0))
    ))
    fig.update_layout(
        title=dict(text="📄 Top Papers by Citations", font=dict(size=16, color='#e0e0ff')),
        xaxis_title='Citations', height=max(380, len(sp)*58),
        yaxis=dict(autorange='reversed'), **CHART_THEME
    )
    return fig


def chart_interests_treemap(interests, name):
    if not interests: return None
    fig = px.treemap(
        names=interests, parents=['']*len(interests), values=[1]*len(interests),
        color=list(range(len(interests))), color_continuous_scale='Purples'
    )
    fig.update_layout(
        title=dict(text="🧠 Research Interests", font=dict(size=16, color='#e0e0ff')),
        height=340, coloraxis_showscale=False, **CHART_THEME
    )
    return fig


def chart_comparison(records):
    names = [r.get('name_faculty', r.get('name','?'))[:18] for r in records]
    fig1  = go.Figure()
    for metric, label, color in [
        ('documents','Documents','#667eea'),
        ('citations','Citations','#764ba2'),
        ('reads',    'Reads',    '#00CCBB')
    ]:
        fig1.add_trace(go.Bar(name=label, x=names,
                               y=[r.get(metric,0) for r in records], marker_color=color))
    fig1.update_layout(barmode='group',
                       title=dict(text='📊 Side-by-Side Comparison', font=dict(size=16,color='#e0e0ff')),
                       height=450, **CHART_THEME)
    fig2 = px.scatter(
        x=[r.get('citations',0) for r in records],
        y=[r.get('documents',0) for r in records],
        size=[max(r.get('reads', r.get('documents',1)),1) for r in records],
        hover_name=[r.get('name_faculty',r.get('name','?')) for r in records],
        color=[r.get('platform','?') for r in records],
        color_discrete_map=PLATFORM_COLORS,
        title='🔵 Research Impact Bubble',
        labels={'x':'Citations','y':'Documents'}
    )
    fig2.update_layout(height=450, **CHART_THEME)
    apply_theme(fig2)
    return fig1, fig2


# ─────────────────────────────────────────────────────────────
# HTML HELPERS
# ─────────────────────────────────────────────────────────────
def platform_badge(platform):
    grad = PLATFORM_GRADIENT.get(platform,'linear-gradient(135deg,#888,#555)')
    icon = PLATFORM_ICONS.get(platform,'🔗')
    return (f"<span style='background:{grad};color:white;padding:5px 14px;"
            f"border-radius:20px;font-size:0.82rem;font-weight:600;"
            f"letter-spacing:0.5px;box-shadow:0 2px 8px rgba(0,0,0,0.3);'>"
            f"{icon} {platform}</span>")

def info_card(label, value, icon='📌'):
    return (f"<div style='background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.12);"
            f"border-radius:14px;padding:1rem 1.2rem;margin:0.4rem 0;'>"
            f"<div style='color:#a0aec0;font-size:0.78rem;font-weight:500;letter-spacing:1px;"
            f"text-transform:uppercase;margin-bottom:4px;'>{icon} {label}</div>"
            f"<div style='color:#e2e8f0;font-size:0.95rem;font-weight:500;'>{value}</div></div>")

def section_header(text, emoji=''):
    st.markdown(
        f"<h3 style='color:#667eea;font-weight:700;margin:1.5rem 0 0.5rem;"
        f"border-left:4px solid #764ba2;padding-left:12px;'>{emoji} {text}</h3>",
        unsafe_allow_html=True)

def tag_cloud(tags, color='#667eea'):
    if not tags: return ''
    html = " ".join([
        f"<span style='background:rgba(102,126,234,0.2);border:1px solid {color};"
        f"border-radius:20px;padding:4px 12px;margin:3px;display:inline-block;"
        f"font-size:0.82rem;color:#e0e0ff;'>{t}</span>"
        for t in tags])
    return f"<div style='margin:0.5rem 0;'>{html}</div>"

def source_badge(source):
    color = '#48bb78' if '✅' in source else '#f6ad55'
    return (f"<div style='background:rgba(72,187,120,0.1);border:1px solid {color};"
            f"border-radius:10px;padding:0.5rem 1rem;margin:0.5rem 0;"
            f"font-size:0.85rem;color:{color};'>📡 Data Source: <b>{source}</b></div>")

def note_banner(note):
    return (f"<div style='background:rgba(246,173,85,0.1);border:1px solid #f6ad55;"
            f"border-radius:10px;padding:0.8rem 1rem;margin:0.5rem 0;"
            f"font-size:0.85rem;color:#f6ad55;'>⚠️ {note}"
            f"<br/><a href='https://developer.ieee.org/member/register' target='_blank' "
            f"style='color:#63b3ed;'>👉 Get Free IEEE API Key</a></div>")

def render_charts(data, faculty_name, platform):
    """Build and render all available charts as tabs"""
    charts = {}
    bar = chart_bar_metrics(data, faculty_name, platform)
    if bar: charts['📊 All Metrics'] = bar
    donut = chart_donut(data, faculty_name, platform)
    if donut: charts['🍩 Distribution'] = donut
    yc = chart_yearly_citations(data.get('citation_by_year',{}), faculty_name)
    if yc: charts['📅 Citation Trend'] = yc
    yp = chart_yearly_pubs(data.get('year_counts',{}), faculty_name)
    if yp: charts['📅 Yearly Papers'] = yp
    ct = chart_content_types(data.get('content_types',{}), faculty_name)
    if ct: charts['📂 Content Types'] = ct
    pc = chart_pub_citations(data.get('pub_records',[]), faculty_name)
    if pc: charts['📄 Top Papers'] = pc
    it = chart_interests_treemap(data.get('interests',[]), faculty_name)
    if it: charts['🧠 Interest Map'] = it

    if charts:
        section_header("Data Visualizations", "📊")
        tabs = st.tabs(list(charts.keys()))
        for tab, (_, fig) in zip(tabs, charts.items()):
            with tab:
                apply_theme(fig)
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("ℹ️ No visualizable data returned yet.")


# ─────────────────────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────────────────────
def main():
    # ── HERO ───────────────────────────────────────────────────
    st.markdown("""
    <div style='text-align:center;padding:2rem 0 1rem;'>
        <div style='font-size:3.5rem;'>🎓</div>
        <h1 style='font-size:2.6rem;font-weight:800;
            background:linear-gradient(135deg,#667eea,#764ba2,#00CCBB);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            margin:0;letter-spacing:-1px;'>Amity Research Intelligence</h1>
        <p style='color:#718096;font-size:1.05rem;margin-top:0.4rem;'>
            Live academic profile analysis · Multi-platform · Professional visualizations
        </p>
    </div>""", unsafe_allow_html=True)

    df = load_faculty_data()

    # ── KPI STRIP ──────────────────────────────────────────────
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("👥 Faculty",        len(df))
    c2.metric("🔗 With Profiles",  int(df['Has_Profile'].sum()))
    c3.metric("🎓 Google Scholar", int((df['Platform']=='Google Scholar').sum()))
    c4.metric("🧪 ResearchGate",   int((df['Platform']=='ResearchGate').sum()))
    c5.metric("⚡ IEEE Xplore",    int((df['Platform']=='IEEE Xplore').sum()))
    st.markdown("<hr/>", unsafe_allow_html=True)

    # ── SESSION STATE ──────────────────────────────────────────
    if 'cmp' not in st.session_state:
        st.session_state.cmp = []

    # ── SIDEBAR ────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("<h2 style='color:#667eea;'>⚙️ Controls</h2>", unsafe_allow_html=True)
        compare_mode = st.checkbox("📊 Enable Comparison Mode")

        st.markdown("<hr/>", unsafe_allow_html=True)
        st.markdown("<p style='color:#a0aec0;font-size:0.85rem;'>🎨 Platform Legend</p>",
                    unsafe_allow_html=True)
        for plat, color in PLATFORM_COLORS.items():
            if plat in ('None','Other'): continue
            st.markdown(
                f"<span style='background:{color};color:white;padding:3px 10px;"
                f"border-radius:12px;font-size:0.78rem;display:inline-block;margin:2px;'>"
                f"{PLATFORM_ICONS.get(plat,'')} {plat}</span>",
                unsafe_allow_html=True)

        st.markdown("<hr/>", unsafe_allow_html=True)
        st.markdown("<p style='color:#a0aec0;font-size:0.78rem;'>🔑 IEEE API Key (optional)</p>",
                    unsafe_allow_html=True)
        ieee_key_input = st.text_input("", placeholder="Paste IEEE API key…",
                                       type="password", label_visibility="collapsed")
        if ieee_key_input:
            global IEEE_API_KEY
            IEEE_API_KEY = ieee_key_input
            st.success("✅ IEEE Key set!")

        if compare_mode and st.session_state.cmp:
            st.markdown("<hr/>", unsafe_allow_html=True)
            st.markdown("<p style='color:#a0aec0;'>Queued for comparison:</p>",
                        unsafe_allow_html=True)
            for r in st.session_state.cmp:
                st.caption(f"• {r.get('name_faculty','?')} [{r.get('platform','')}]")
            if st.button("🗑️ Clear All"):
                st.session_state.cmp = []
                st.rerun()

    # ── DIRECTORY ──────────────────────────────────────────────
    section_header("Faculty Directory", "🗂️")
    plat_opts = ['All'] + sorted(df['Platform'].unique().tolist())
    sel_plat  = st.selectbox("Filter by platform:", plat_opts)
    view_df   = df if sel_plat=='All' else df[df['Platform']==sel_plat]
    st.dataframe(
        view_df[['Sr No','Faculty Name','School','Platform','Profile Link']],
        use_container_width=True, height=260)
    st.markdown("<hr/>", unsafe_allow_html=True)

    # ── SEARCH & ANALYZE ───────────────────────────────────────
    section_header("Analyze Author Profile", "🔍")
    search = st.text_input("",
        placeholder="🔎  Type faculty name… e.g.  Atul,  Murari,  Bhanu,  Dhirendra")

    if search:
        matches = df[df['Faculty Name'].str.contains(search, case=False, na=False)]
        if matches.empty:
            st.warning("❌ No faculty matched. Try a different name.")
        else:
            for _, row in matches.iterrows():
                plat = row['Platform']
                icon = PLATFORM_ICONS.get(plat,'🔗')

                with st.expander(
                    f"{icon}  {row['Faculty Name'].strip()}  ·  {row['School']}  ·  {plat}",
                    expanded=True):

                    h1, h2, h3 = st.columns([2,1.5,2])
                    with h1:
                        st.markdown(info_card("Faculty Name", row['Faculty Name'].strip(), "👤"),
                                    unsafe_allow_html=True)
                        st.markdown(info_card("School", row['School'], "🏛️"),
                                    unsafe_allow_html=True)
                    with h2:
                        st.markdown("<br/>", unsafe_allow_html=True)
                        st.markdown(platform_badge(plat), unsafe_allow_html=True)
                    with h3:
                        if row['Has_Profile']:
                            st.markdown(
                                info_card("Profile",
                                    f"<a href='{row['Profile Link']}' target='_blank' "
                                    f"style='color:#63b3ed;'>🔗 Open Profile</a>","🌐"),
                                unsafe_allow_html=True)

                    if not row['Has_Profile']:
                        st.info("ℹ️ No profile link available for this faculty.")
                        continue

                    st.markdown("<br/>", unsafe_allow_html=True)
                    if st.button(f"🚀  Fetch Live Data from {plat}",
                                 key=f"btn_{row['Sr No']}"):
                        with st.spinner(f"🔄  Connecting to {plat}…"):
                            data = fetch_author_data(row['Profile Link'], plat)

                        faculty_name = row['Faculty Name'].strip()

                        # ══════════════════════════════════════
                        # MANUAL ENTRY MODE (IEEE Layer 5)
                        # ══════════════════════════════════════
                        if data['status'] == 'manual_required':
                            st.markdown(f"""
                            <div style='background:rgba(246,173,85,0.12);border:1px solid #f6ad55;
                            border-radius:14px;padding:1.2rem 1.5rem;margin:0.5rem 0;'>
                                <b style='color:#f6ad55;font-size:1rem;'>⚠️ IEEE Blocked All Automated Access</b><br/>
                                <span style='color:#e0e0ff;font-size:0.9rem;'>
                                Enter data manually from the
                                <a href='{data["profile_url"]}' target='_blank' style='color:#63b3ed;'>
                                🔗 IEEE Profile Page</a> → then click Save & Visualize.
                                </span>
                            </div>""", unsafe_allow_html=True)

                            with st.form(key=f"manual_ieee_{row['Sr No']}"):
                                st.markdown(
                                    "<p style='color:#a0aec0;font-size:0.85rem;'>"
                                    "📋 Copy values directly from the open IEEE profile page:</p>",
                                    unsafe_allow_html=True)
                                mc1, mc2 = st.columns(2)
                                with mc1:
                                    m_name = st.text_input("👤 Author Name",   value=faculty_name)
                                    m_aff  = st.text_input("🏛️ Affiliation",   value="Amity University")
                                    m_docs = st.number_input("📄 Total Papers", min_value=0, value=0, step=1)
                                with mc2:
                                    m_cit  = st.number_input("📊 Total Citations",     min_value=0,   value=0,   step=1)
                                    m_cpd  = st.number_input("📈 Avg Citations/Paper", min_value=0.0, value=0.0, step=0.1)
                                    m_area = st.text_input("🧠 Research Areas",
                                                           placeholder="AI, ML, IoT (comma separated)")

                                submitted = st.form_submit_button("💾 Save & Visualize")
                                if submitted:
                                    interests   = [x.strip() for x in m_area.split(',') if x.strip()]
                                    manual_data = {
                                        'status':            'success',
                                        'source':            'Manual Entry (IEEE Blocked) 📝',
                                        'platform':          'IEEE Xplore',
                                        'name':              m_name,
                                        'affiliation':       m_aff,
                                        'documents':         int(m_docs),
                                        'citations':         int(m_cit),
                                        'citations_per_doc': float(m_cpd),
                                        'interests':         interests,
                                        'year_counts':       {},
                                        'content_types':     {},
                                        'pub_records':       [],
                                        'profile_url':       data['profile_url']
                                    }
                                    st.markdown(source_badge(manual_data['source']),
                                                unsafe_allow_html=True)
                                    st.markdown(f"""
                                    <div style='background:linear-gradient(135deg,
                                        rgba(0,98,155,0.2),rgba(0,79,128,0.2));
                                        border:1px solid rgba(0,98,155,0.4);
                                        border-radius:18px;padding:1.5rem 2rem;margin:1rem 0;'>
                                        <div style='font-size:1.4rem;font-weight:700;color:#e2e8f0;'>
                                            ⚡ {m_name}</div>
                                        <div style='color:#a0aec0;margin-top:6px;'>🏛️ {m_aff}</div>
                                        <div style='margin-top:10px;'>{platform_badge('IEEE Xplore')}</div>
                                    </div>""", unsafe_allow_html=True)

                                    cc1, cc2, cc3 = st.columns(3)
                                    cc1.metric("📄 Papers",    int(m_docs))
                                    cc2.metric("📊 Citations", int(m_cit))
                                    cc3.metric("📈 Cit/Paper", float(m_cpd))

                                    if interests:
                                        section_header("Research Areas","🧠")
                                        st.markdown(tag_cloud(interests,'#00629B'),
                                                    unsafe_allow_html=True)

                                    render_charts(manual_data, m_name, 'IEEE Xplore')

                                    if compare_mode:
                                        save = {**manual_data, 'name_faculty': faculty_name}
                                        if save not in st.session_state.cmp:
                                            st.session_state.cmp.append(save)
                                            st.success("✅ Added to comparison!")

                            st.markdown(f"""
                            <div style='background:rgba(99,179,237,0.08);border:1px solid #63b3ed;
                            border-radius:12px;padding:0.8rem 1.2rem;margin-top:0.5rem;
                            font-size:0.85rem;color:#63b3ed;'>
                                🔑 <b>Permanent fix:</b> Register free IEEE API key →
                                <a href='https://developer.ieee.org/member/register'
                                target='_blank' style='color:#63b3ed;'>
                                developer.ieee.org/member/register</a> → paste in sidebar
                            </div>""", unsafe_allow_html=True)

                        # ══════════════════════════════════════
                        # SUCCESS — Normal display
                        # ══════════════════════════════════════
                        elif data['status'] == 'success':
                            src  = data.get('source','')
                            note = data.get('_note','')
                            if src:  st.markdown(source_badge(src),  unsafe_allow_html=True)
                            if note: st.markdown(note_banner(note),  unsafe_allow_html=True)

                            email_part = (
                                f"&nbsp;&nbsp;|&nbsp;&nbsp;✉️ {data.get('email_domain','')}"
                                if data.get('email_domain') else '')
                            st.markdown(f"""
                            <div style='background:linear-gradient(135deg,
                                rgba(102,126,234,0.15),rgba(118,75,162,0.15));
                                border:1px solid rgba(255,255,255,0.15);
                                border-radius:18px;padding:1.5rem 2rem;margin:1rem 0;'>
                                <div style='font-size:1.4rem;font-weight:700;color:#e2e8f0;'>
                                    👤 {data.get('name', faculty_name)}</div>
                                <div style='color:#a0aec0;margin-top:6px;'>
                                    🏛️ {data.get('affiliation','N/A')}{email_part}</div>
                                <div style='margin-top:10px;'>{platform_badge(plat)}</div>
                            </div>""", unsafe_allow_html=True)

                            if data.get('interests'):
                                section_header("Research Interests","🧠")
                                st.markdown(tag_cloud(data['interests']), unsafe_allow_html=True)
                            if data.get('coauthors'):
                                section_header("Co-Authors","🤝")
                                st.markdown(tag_cloud(data['coauthors'],'#00CCBB'),
                                            unsafe_allow_html=True)

                            render_charts(data, faculty_name, plat)

                            if compare_mode:
                                save = {**data, 'name_faculty': faculty_name}
                                if save not in st.session_state.cmp:
                                    st.session_state.cmp.append(save)
                                    st.success("✅ Added to comparison dashboard")

                        elif data['status'] == 'blocked':
                            st.warning(f"⚠️ {data['message']}")
                            st.info("💡 Rate-limited. Wait 30s and retry.")
                        else:
                            st.error(f"❌ {data.get('message','Unknown error')}")

    # ── COMPARISON DASHBOARD ───────────────────────────────────
    if compare_mode and len(st.session_state.cmp) >= 2:
        st.markdown("<hr/>", unsafe_allow_html=True)
        section_header("Comparison Dashboard","🏆")
        cdf  = pd.DataFrame(st.session_state.cmp)
        show = [c for c in ['name_faculty','platform','documents','citations',
                             'reads','recommendations','followers','citations_per_doc']
                if c in cdf.columns]
        st.dataframe(cdf[show], use_container_width=True)
        f1, f2 = chart_comparison(st.session_state.cmp)
        col1, col2 = st.columns(2)
        with col1:
            apply_theme(f1); st.plotly_chart(f1, use_container_width=True)
        with col2:
            apply_theme(f2); st.plotly_chart(f2, use_container_width=True)
        st.download_button("💾 Export Comparison CSV",
                           cdf.to_csv(index=False), "amity_comparison.csv","text/csv")

    # ── FOOTER ─────────────────────────────────────────────────
    st.markdown("<hr/>", unsafe_allow_html=True)
    with st.expander("📋 Faculty With Profiles", expanded=False):
        st.dataframe(df[df['Has_Profile']][['Faculty Name','School','Platform','Profile Link']],
                     use_container_width=True)
    with st.expander("📋 Faculty Without Profiles", expanded=False):
        st.dataframe(df[~df['Has_Profile']][['Faculty Name','School']], use_container_width=True)

    st.markdown("""
    <div style='text-align:center;padding:2rem 0 1rem;color:#4a5568;font-size:0.85rem;'>
        Amity Research Intelligence · Streamlit · Google Scholar · ResearchGate · IEEE Xplore
    </div>""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
