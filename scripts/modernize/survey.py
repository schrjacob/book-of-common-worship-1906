"""List archaic word forms found in the blocks that will be modernized (helper for building the word maps)."""
import re, collections, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from fixed import is_fixed

ROOT = Path(__file__).resolve().parents[2]
text = (ROOT / 'manuscript' / 'book-of-common-worship-1906.md').read_text(encoding='utf-8')
blocks = [b.strip() for b in re.split(r'\n\s*\n', text) if b.strip()]
ctx = []
eth, est, other = collections.Counter(), collections.Counter(), collections.Counter()
nfix = nmod = 0
for b in blocks:
    m = re.match(r'^(#{1,6}) (.*)$', b)
    if m:
        lv = len(m.group(1)); ctx = ctx[:lv - 1] + [''] * max(0, lv - 1 - len(ctx)); ctx = ctx[:lv - 1] + [m.group(2)]
        continue
    if is_fixed(b, ctx):
        nfix += 1; continue
    nmod += 1
    for w in re.findall(r"[A-Za-z]+", re.sub(r'<!--.*?-->', '', b)):
        lw = w.lower()
        if lw.endswith('eth') and len(lw) > 4: eth[lw] += 1
        elif lw.endswith('est') and len(lw) > 4: est[lw] += 1
        elif lw in ('thee', 'thou', 'thy', 'thine', 'thyself', 'ye', 'hath', 'doth', 'hast', 'dost', 'art', 'wilt',
                    'shalt', 'wast', 'canst', 'didst', 'unto', 'vouchsafe', 'ghost', 'amongst', 'whilst'):
            other[lw] += 1
print('fixed blocks', nfix, 'modernized blocks', nmod)
print('ETH', sorted(eth.items()))
print('EST', sorted(est.items()))
print('OTHER', sorted(other.items()))
