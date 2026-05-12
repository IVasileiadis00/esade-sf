import pandas as pd, openpyxl, re
from difflib import SequenceMatcher

STOXX_FILE = r'C:\Users\ionva\Desktop\Sustainable Finance Project\.claude\worktrees\tender-merkle-cddcc3\STOXX600_Outperformers_5Y_10Y.xlsx'
CSV_FILE   = r'C:\Users\ionva\Desktop\Sustainable Finance Project\.claude\worktrees\tender-merkle-cddcc3\data\provided\equityBicsV2.csv'
OUT_FILE   = r'C:\Users\ionva\Desktop\Sustainable Finance Project\.claude\worktrees\tender-merkle-cddcc3\data\provided\universe_170.csv'

EXCHANGE_MAP = {
    'DE':'.DE','SE':'.ST','NL':'.AS','GB':'.L','CH':'.SW','FR':'.PA',
    'IT':'.MI','ES':'.MC','NO':'.OL','FI':'.HE','DK':'.CO','BE':'.BR',
    'AT':'.VI','PL':'.WA','PT':'.LS','IE':'.IR','LU':'.LU',
}

def stoxx_to_yf(t):
    if not t or '-' not in str(t):
        return None
    part, exch = str(t).rsplit('-', 1)
    return part.replace('.', '-') + EXCHANGE_MAP.get(exch, '.' + exch)

def normalize(s):
    s = str(s).lower().strip()
    # Replace slashes with spaces so "SA/NV" becomes "SA NV"
    s = s.replace('/', ' ')
    # Collapse abbreviation dots: n.v. → nv, s.p.a. → spa
    s = re.sub(r'([a-z])\.([a-z])\.?', r'\1\2', s)
    # Remove all remaining punctuation
    s = re.sub(r'[^\w\s]', '', s)
    # Remove corporate suffixes and noise words
    s = re.sub(r'\b(nv|sa|spa|plc|ag|ab|asa|oyj|se|ltd|inc|group|holding|holdings|'
               r'class [ab]|aktiengesellschaft|abp|ruckversicherungs|gesellschaft|'
               r'spolka|akcyjna|polska|banca|banco|bank|banque|cantonale|'
               r'versicherungs|assurances|assicurazioni|financiere|financiero|'
               r'compagnie|generali|internationale)\b', '', s)
    return re.sub(r'\s+', ' ', s).strip()

# Load Excel
wb = openpyxl.load_workbook(STOXX_FILE)
ws170 = wb['170 Outperformers ']
rows170 = [(r[0], r[2], r[3], r[4]) for r in ws170.iter_rows(min_row=2, max_row=171, values_only=True) if r[2]]

ws600 = wb['Stoxx 600 List']
name_to_stoxx = {}
for r in ws600.iter_rows(min_row=7, max_row=611, values_only=True):
    if r[0] and r[1]:
        name_to_stoxx[r[0].lower().strip()] = r[1]

# Load equityBicsV2 - one row per company
print('Loading equityBicsV2...')
df = pd.read_csv(CSV_FILE, low_memory=False)
df_co = df.drop_duplicates('idBbCompany').copy()
df_co['_norm'] = df_co['idBbGlobalCompanyName'].fillna('').apply(normalize)
norm_lookup = df_co.drop_duplicates('_norm').set_index('_norm')[['idBbCompany', 'idBbGlobalCompanyName']].to_dict('index')
all_norms = list(norm_lookup.keys())

records = []
unmatched = []

for rank, company, r5, r10 in rows170:
    stoxx_t = name_to_stoxx.get(company.lower().strip(), '')
    yf_t = stoxx_to_yf(stoxx_t)
    n = normalize(company)
    idc, matched_name = None, None

    # 1. Exact normalized name match
    if n in norm_lookup:
        idc = norm_lookup[n]['idBbCompany']
        matched_name = norm_lookup[n]['idBbGlobalCompanyName']

    # 2. Fuzzy name match (ratio > 0.85)
    if not idc:
        best_score, best_norm = 0, None
        for candidate in all_norms:
            if abs(len(n) - len(candidate)) > 8:
                continue
            score = SequenceMatcher(None, n, candidate).ratio()
            if score > best_score:
                best_score, best_norm = score, candidate
        # Require first word to also match (avoids e.g. Hiab → Hifab false positives)
        first_word_match = n.split()[0][:4] == best_norm.split()[0][:4] if n and best_norm else False
        if best_score > 0.85 and first_word_match:
            idc = norm_lookup[best_norm]['idBbCompany']
            matched_name = norm_lookup[best_norm]['idBbGlobalCompanyName']

    records.append({
        'rank': rank, 'company': company,
        'return_5y_pct': r5, 'return_10y_pct': r10,
        'stoxx_ticker': stoxx_t, 'yf_ticker': yf_t,
        'idBbCompany': idc, 'matched_csv_name': matched_name
    })
    if not idc:
        unmatched.append((rank, company))

df_out = pd.DataFrame(records)
matched_count = int(df_out['idBbCompany'].notna().sum())
print(f'Matched: {matched_count}/170')
print(f'Unmatched ({len(unmatched)}):')
for r, c in unmatched:
    print(f'  Rank {r}: {c}')

print()
print('--- Full verification table ---')
print(df_out[['rank', 'company', 'matched_csv_name', 'yf_ticker']].to_string(index=False))

df_out.to_csv(OUT_FILE, index=False)
print(f'\nSaved to {OUT_FILE}')
