"""
First, mechanical pass of the light modernization (run once; the result was then
revised by hand, block by block). Kept for the record of what was changed
systematically.

    python scripts/modernize/first_pass.py

Writes manuscript/book-of-common-worship-1906-light.md from the original,
leaving fixed blocks (see fixed.py) untouched.
"""
import re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from fixed import is_fixed

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'manuscript' / 'book-of-common-worship-1906.md'
DST = ROOT / 'manuscript' / 'book-of-common-worship-1906-light.md'

WORDS = {
    # pronouns
    'thee': 'you', 'thou': 'you', 'thy': 'your', 'thyself': 'yourself', 'ye': 'you',
    # second-person verb forms
    'hast': 'have', 'didst': 'did', 'dost': 'do', 'wilt': 'will', 'canst': 'can', 'art': 'are',
    'shalt': 'shall', 'wast': 'were', 'mayest': 'may', 'wouldest': 'would', 'gavest': 'gave',
    'abidest': 'abide', 'bestowest': 'bestow', 'bringest': 'bring', 'changest': 'change', 'chastenest': 'chasten',
    'commandest': 'command', 'coverest': 'cover', 'declarest': 'declare', 'delightest': 'delight',
    'desirest': 'desire', 'despisest': 'despise', 'doest': 'do', 'dwellest': 'dwell', 'feedest': 'feed',
    'fillest': 'fill', 'foreseest': 'foresee', 'forgettest': 'forget', 'forgivest': 'forgive', 'givest': 'give',
    'grantest': 'grant', 'hatest': 'hate', 'healest': 'heal', 'hearest': 'hear', 'holdest': 'hold',
    'increasest': 'increase', 'keepest': 'keep', 'knowest': 'know', 'livest': 'live', 'lovest': 'love',
    'makest': 'make', 'openest': 'open', 'pointest': 'point', 'pourest': 'pour', 'providest': 'provide',
    'receivest': 'receive', 'redeemest': 'redeem', 'reignest': 'reign', 'resistest': 'resist', 'riddest': 'rid',
    'rulest': 'rule', 'seest': 'see', 'spreadest': 'spread', 'stillest': 'still', 'thinkest': 'think',
    'turnest': 'turn',
    # third-person verb forms
    'hath': 'has', 'doth': 'does', 'becometh': 'becomes', 'believeth': 'believes', 'belongeth': 'belongs',
    'cometh': 'comes', 'comforteth': 'comforts', 'desireth': 'desires', 'dwelleth': 'dwells', 'fadeth': 'fades',
    'giveth': 'gives', 'liveth': 'lives', 'loveth': 'loves', 'maketh': 'makes', 'panteth': 'pants',
    'reigneth': 'reigns', 'remaineth': 'remains', 'riseth': 'rises', 'seemeth': 'seems', 'shineth': 'shines',
    'standeth': 'stands', 'tempteth': 'tempts', 'waiteth': 'waits', 'waketh': 'wakes',
    # other archaisms
    'unto': 'to', 'amongst': 'among',
    # spelling
    'honour': 'honor', 'honoured': 'honored', 'honourable': 'honorable', 'labour': 'labor', 'labours': 'labors',
    'laboured': 'labored', 'labourers': 'laborers', 'saviour': 'savior', 'favour': 'favor', 'favourable': 'favorable',
    'favourably': 'favorably', 'endeavour': 'endeavor', 'endeavours': 'endeavors', 'endeavoured': 'endeavored',
    'endeavouring': 'endeavoring', 'candour': 'candor', 'neighbour': 'neighbor', 'neighbours': 'neighbors',
    'succour': 'succor', 'fulness': 'fullness', 'behaviour': 'behavior', 'vapour': 'vapor', 'harbour': 'harbor',
    'to-day': 'today', 'to-morrow': 'tomorrow',
}


def match_case(src, repl):
    if src.isupper() and len(src) > 1:
        return repl.upper()
    if src[0].isupper():
        return repl[0].upper() + repl[1:]
    return repl


def thine(m):
    word, nxt = m.group(1), m.group(2)
    # "Thine" before a word beginning with a letter is a possessive adjective (Thine elect -> Your elect);
    # otherwise it stands alone (is Thine -> is Yours)
    if re.match(r'\s+(own|[a-z]|[A-Z][a-z])', nxt) and not re.match(r'\s+(for|and|in|is|both|alone|now|to)\b', nxt):
        rep = 'your'
    else:
        rep = 'yours'
    return match_case(word, rep) + nxt


def modernize(text):
    text = re.sub(r'\b(Holy) Ghost\b', r'\1 Spirit', text)
    text = re.sub(r'\b([Tt]hine)(\s*\S*)', thine, text)
    def word(m):
        w = m.group(0)
        rep = WORDS.get(w.lower())
        return match_case(w, rep) if rep else w
    return re.sub(r"[A-Za-z]+(?:-[a-z]+)?", word, text)


def main():
    text = SRC.read_text(encoding='utf-8')
    parts = re.split(r'(\n\s*\n)', text)          # keep separators so the layout is preserved exactly
    ctx = []
    out = []
    changed = 0
    for part in parts:
        b = part.strip()
        if not b or re.fullmatch(r'\s*', part):
            out.append(part); continue
        m = re.match(r'^(#{1,6}) (.*)$', b)
        if m and '\n' not in b:
            lv = len(m.group(1)); ctx = (ctx + [''] * lv)[:lv - 1] + [m.group(2)]
            out.append(part); continue
        if is_fixed(b, ctx):
            out.append(part); continue
        new = modernize(part)
        changed += new != part
        out.append(new)
    DST.write_text(''.join(out), encoding='utf-8')
    print('modernized blocks:', changed)


if __name__ == '__main__':
    main()
