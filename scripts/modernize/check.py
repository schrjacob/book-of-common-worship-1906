"""QA for the light manuscript: fixed blocks unchanged; leftover archaisms in modernized blocks."""
import re, sys, importlib.util
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from fixed import is_fixed

ROOT = Path(__file__).resolve().parents[2]
def blocks(p):
    t = re.sub(r'<!--.*?-->', '', p.read_text(encoding='utf-8'))
    return [b.strip() for b in re.split(r'\n\s*\n', t) if b.strip()]
O = blocks(ROOT / 'manuscript' / 'book-of-common-worship-1906.md')
L = blocks(ROOT / 'manuscript' / 'book-of-common-worship-1906-light.md')
assert len(O) == len(L)

orig_restored = set()
for f in sorted((Path(__file__).parent / 'revisions').glob('part*.py')):
    src = f.read_text(encoding='utf-8')
    orig_restored |= {int(m) for m in re.findall(r'^(\d+): ORIGINAL', src, re.M)}

ARCH = re.compile(r"\b(thee|thou|thy|thine|thyself|ye|hath|doth|hast|dost|art|wilt|shalt|canst|didst|wouldst|wouldest|"
                  r"beseech\w*|vouchsafe\w*|unto|whereby|wherein|whereof|wherewith|whither|hither|thereof|henceforth|"
                  r"succou?r|nigh|amongst|whilst|lest|[a-z]+eth|[a-z]+est)\b", re.I)
OK_EST = {'best', 'rest', 'least', 'priest', 'earnest', 'honest', 'interest', 'greatest', 'nearest', 'dearest', 'surest',
          'manifest', 'modest', 'tempest', 'request', 'highest', 'holiest', 'forest', 'forests', 'harvest', 'protest',
          'behest', 'conquest', 'midst', 'guest', 'west', 'chest', 'test', 'quest', 'invest', 'unrest', 'arrest',
          'suggest', 'lowest', 'deepest', 'purest', 'humblest', 'fullest', 'largest', 'strongest', 'latest', 'noblest',
          'wisest', 'blessedest', 'contest', 'digest', 'infest', 'molest', 'attest', 'detest', 'crest', 'jest', 'nest',
          'pest', 'vest', 'zest', 'lest', 'eldest', 'oldest', 'tenderest', 'sweetest', 'richest', 'utmost', 'most',
          'truest', 'fairest', 'kindest', 'meekest', 'loveliest', 'lowliest', 'dimmest', 'brightest', 'darkest'}
OK_ETH = {'beneath', 'breath', 'teeth', 'seth', 'nazareth', 'elizabeth', 'death', 'twentieth', 'hundredth', 'tenth',
          'fifth', 'fourth', 'lengeth', 'length', 'strength', 'meth', 'teeth', 'beth', 'ninth'}
problems = 0
ctx = []
for i, (o, l) in enumerate(zip(O, L)):
    m = re.match(r'^(#{1,6}) (.*)$', o)
    if m and '\n' not in o:
        lv = len(m.group(1)); ctx = (ctx + [''] * lv)[:lv - 1] + [m.group(2)]
        continue
    if is_fixed(o, ctx) or i in orig_restored:
        if o != l:
            print(f'[{i}] FIXED BLOCK CHANGED'); problems += 1
        continue
    hits = []
    for mm in ARCH.finditer(l):
        w = mm.group(0).lower()
        if w.endswith('est') and (w in OK_EST or len(w) <= 4): continue
        if w.endswith('eth') and w in OK_ETH: continue
        hits.append(mm.group(0))
    for pat in [r'\bYour (shall|is|be|for|and)\b', r'\bYou (is|was|has|does)\b', r'\byou (are|have) [^.]*\bYour\b',
                r'\bdo not let \w+ to\b', r'\bO YOU\b', r'  ', r'\bYou, who did\b', r'\b(he|she|it) (do|have)\b']:
        for mm in re.finditer(pat, l):
            if pat == r'\bO YOU\b': continue
            hits.append('«' + mm.group(0) + '»')
    if hits:
        print(f'[{i}] {sorted(set(hits))} :: {l[:110]}')
        problems += 1
print('blocks with notes:', problems)
