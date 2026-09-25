"""
Second pass of the light modernization: hand revisions, block by block.

    python scripts/modernize/apply_revisions.py

Starts from the first pass (first_pass.py) and replaces individual blocks with the
hand-revised text in revisions/part*.py. Each part defines REV = {block_index: text}.
The special value ORIGINAL restores the 1906 wording unchanged (used for Scripture
that the first pass should not have touched). Block indices count the blank-line
separated blocks of the original manuscript, starting at 0.

After the modernization is complete the light manuscript is edited directly; these
scripts are kept as a record of how it was produced.
"""
import importlib.util, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import first_pass

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = 'ORIGINAL'


def load_revisions():
    rev = {}
    for f in sorted((Path(__file__).parent / 'revisions').glob('part*.py')):
        spec = importlib.util.spec_from_file_location(f.stem, f)
        mod = importlib.util.module_from_spec(spec)
        mod.ORIGINAL = ORIGINAL
        spec.loader.exec_module(mod)
        for k in mod.REV:
            if k in rev:
                raise SystemExit(f'block {k} revised twice ({f.name})')
        rev.update(mod.REV)
    return rev


POST = [   # common constructions, applied to modernized blocks that were not hand-revised
    (r', we (most |humbly )?beseech You([,;:])', r', we \1pray\2'),
    (r'\bwe (most humbly |humbly |most heartily )?beseech You to\b', r'we \1ask You to'),
    (r'\bWe (most humbly |humbly |most heartily )?beseech You to\b', r'We \1ask You to'),
    (r'\bMost heartily we beseech You to\b', 'Most heartily we ask You to'),
    (r'\bwe (humbly )?beseech You, that\b', r'we \1pray that'),
    (r'\bWe (humbly )?beseech You, that\b', r'We \1pray that'),
    (r'\bwe beseech You, grant\b', 'we pray, grant'),
    (r'\bbeseeching You\b', 'asking You'), (r'\bbeseech Your Majesty\b', 'call upon Your Majesty'),
    (r'\bdid (give|send|come|turn|enlighten|order|show|love|take|raise|humble|weep|appoint)\b',
     lambda m: {'give': 'gave', 'send': 'sent', 'come': 'came', 'turn': 'turned', 'enlighten': 'enlightened',
                'order': 'ordered', 'show': 'showed', 'love': 'loved', 'take': 'took', 'raise': 'raised',
                'humble': 'humbled', 'weep': 'wept', 'appoint': 'appointed'}[m.group(1)]),
    (r'\bwho do (inhabit|bid|gladden|govern)\b', r'who \1'),
    (r'\bBe You\b', 'Be'), (r'\bbe You\b', 'be'), (r'\bDo You ([a-z])', lambda m: m.group(1).upper()), (r'\bdo You (?=[a-z])', ''),
    (r'\bOpen You\b', 'Open'), (r'\bsend You\b', 'send'), (r'\bKeep You\b', 'Keep'), (r'\bspeak You\b', 'speak'),
    (r'\bYou only wise God\b', 'the only wise God'),
    (r'\bthem that\b', 'those who'), (r'\bthose that (?=[a-z]+[^s ]*\b)', 'those who '),
    (r'\bsuccor\b', 'help'), (r'\bfulfil\b', 'fulfill'),
    (r'\bwhereby\b', 'by which'), (r'\bwherein\b', 'in which'), (r'\bwhereof\b', 'of which'), (r'\bwherewith\b', 'with which'),
    (r'\ban (humble|holy|unity)\b', r'a \1'),
    (r'\bsuffer (him|us|them) not\b', r'do not let \1'), (r'\bsuffer them never to be\b', 'never let them be'),
    (r'\bif it be Your will\b', 'if it is Your will'),
    (r'(^|[.;:] )(Remember|Despise|Reckon) not\b', lambda m: m.group(1) + 'Do not ' + m.group(2).lower()), (r'\b(Let|let) not\b', lambda m: ('Do not let' if m.group(1) == 'Let' else 'do not let')),
    (r'\bvouchsafe us\b', 'grant us'), (r'\b[Vv]ouchsafe to (?=us|Your)', 'Grant to '), (r'\bvouchsafe\b', 'be pleased to grant'),
]


def post_rules(text):
    for pat, rep in POST:
        text = re.sub(pat, rep, text)
    return text


def main():
    first_pass.main()
    orig = first_pass.SRC.read_text(encoding='utf-8')
    light = first_pass.DST.read_text(encoding='utf-8')
    o_parts = re.split(r'(\n\s*\n)', orig)
    l_parts = re.split(r'(\n\s*\n)', light)
    assert len(o_parts) == len(l_parts)
    rev = load_revisions()
    idx = -1
    ctx = []
    for n, part in enumerate(o_parts):
        if not re.sub(r'<!--.*?-->', '', part, flags=re.S).strip():
            continue                                   # separators and comment-only blocks are not counted
        idx += 1
        b = part.strip()
        m = re.match(r'^(#{1,6}) (.*)$', b)
        if m and '\n' not in b:
            lv = len(m.group(1)); ctx = (ctx + [''] * lv)[:lv - 1] + [m.group(2)]
        elif idx not in rev and not first_pass.is_fixed(b, ctx):
            l_parts[n] = post_rules(l_parts[n])
        if idx in rev:
            new = rev[idx]
            if new == ORIGINAL:
                l_parts[n] = part
            else:
                # keep any leading page marker / review comment of the original block
                lead = re.match(r'^((?:\s*<!--.*?-->\s*)*)', part).group(1)
                l_parts[n] = (lead if not new.lstrip().startswith('<!--') else '') + new.strip('\n')
    first_pass.DST.write_text(''.join(l_parts), encoding='utf-8')
    print('hand revisions applied:', len(rev))


if __name__ == '__main__':
    main()
