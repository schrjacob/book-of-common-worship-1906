"""
Which blocks of the manuscript must stay word-for-word in the light edition.

Holy Scripture keeps the exact KJV wording, and these traditional texts are also
left as printed: the Lord's Prayer, the Apostles' Creed, the Gloria Patri, the
canticles, the marriage vows and ring formula, metrical hymns, and the Scripture
benedictions and ascriptions.

is_fixed(block, context) -> True if the block must be copied unchanged.
`context` is the list of enclosing headings (outermost first) for the block.
"""
import re

# whole sections (any heading in the chain) whose contents are Scripture or fixed texts
FIXED_SECTIONS = [
    r'^The Psalter$',                       # the Psalter (KJV)
    r'^Ancient Hymns and Canticles$',
    r'^Psalm ',                              # burial psalms
    r'^1 Corinthians xv',                    # burial lessons
    r'^St\. John xiv',
    r'^Revelation xxi\.',
    r'^2 Samuel xii',
    r'^St\. Mark x\.',
    r'^Revelation xxii\. 4',
    r'^Gloria in Excelsis',
    r'^Table of Contents$',
]

# individual blocks recognised by their opening words
FIXED_STARTS = [
    # Lord's Prayer, Creed, Gloria Patri
    'OUR Father which art in heaven',
    'I BELIEVE in God the Father Almighty', 'And in Jesus Christ His only Son',
    'I believe in the Holy Ghost; The Holy Catholic Church', '[^creed',
    'Glory be to the Father', 'GLORY be to the Father', 'As it was in the beginning',
    # Gloria in Excelsis (Evening Service)
    'GLORY be to God on high', 'We praise Thee, we bless Thee', 'O Lord God, heavenly King',
    'O Lord, the only-begotten Son', 'That takest away the sins', 'Thou that takest away',
    'Thou that sittest at the right hand', 'For Thou only art holy', 'Thou only, O Christ',
    # marriage vows and ring
    'I, M., take thee', 'I, N., take thee', 'THIS Ring I give thee',
    # hymns and metrical texts
    'Praise God, from whom all blessings flow', 'O WORD of God Incarnate', 'The Church from her dear Master',
    'It floateth like a banner', 'O make Thy Church, dear Saviour', 'ALL people that on earth do dwell',
    'The Lord ye know is God indeed', 'O enter then His gates', 'For why? The Lord our God is good',
    'LORD Jesus, be our holy Guest',
    # versicles and responses drawn from Scripture, and the Sursum Corda / Sanctus
    'Create in us a clean heart', '*Minister.* Now bless the Lord', '*Answer.* And praise His glorious',
    '*Minister.* O give thanks unto the Lord', '*Answer.* For His mercy endureth',
    '*Minister.* Blessed are the undefiled', '*Answer.* Order my steps', '*Minister.* Blessed are they that keep',
    '*Answer.* With my whole heart', '*Minister.* Draw nigh to God', '*Answer.* Bow down Thine ear',
    '*Minister.* Therefore will the Lord wait', '*Answer.* Let Thy mercy, O Lord',
    '*Minister.* The Lord be with you', '*People.* And with thy spirit', '*Minister.* Lift up your hearts',
    '*People.* We lift them up', '*Minister.* Let us give thanks', '*People.* It is meet and right',
    'HOLY, HOLY, HOLY, Lord God of Hosts',
    # Commandments, Beatitudes, Summary of the Law
    'GOD spake all these words', 'I am the Lord thy God, which have brought', 'Thou shalt ', 'Remember the Sabbath-day',
    'Honour thy father and thy mother', '*Lord, have mercy upon us', 'Hear also what our Lord Jesus Christ saith',
    'BLESSED are the poor in spirit', 'Blessed are ', '*Lord, be gracious unto us', '*Grant unto us Thy Holy Spirit, O God, and enable',
    # benedictions and ascriptions (Scripture)
    'THE grace of the Lord Jesus Christ', 'THE peace of God, which passeth', 'NOW the God of peace',
    'NOW unto Him', 'NOW unto the blessed', 'NOW unto the God of all grace', 'UNTO Him that loved us',
    'BLESSING, and honour, and glory', 'The Lord bless you and keep you', 'The Lord lift up His countenance',
    'Both now and in the life everlasting', 'WHOM therefore God hath joined',
    # other Scripture sentences and quotations standing alone
    'THE Lord gave, and the Lord hath taken away', 'I HEARD a voice from heaven', 'MAN that is born of a woman',
    'I AM the Resurrection and the Life', 'For we know that if our earthly house', '"All power is given unto Me',
    'THE earth is the Lord\'s', 'For he hath founded it upon the seas', 'Who shall ascend into the hill',
    'He that hath clean hands', 'He shall receive the blessing', 'This is the generation of them',
    'Lift up your heads', 'Who is this King of glory', 'The Lord strong and mighty', 'The Lord of hosts: he is',
    'BLESSED be thou, Lord God of Israel', 'Thine, O Lord, is the greatness', 'Thine is the kingdom, O Lord',
    'Both riches and honour', 'And in thine hand is power', 'Now therefore, our God, we thank thee',
    'But who am I, and what is my people', 'For all things come of thee', 'For we are strangers before thee',
    'Our days on the earth are as a shadow', 'O Lord, our God, all this store', 'I know also, my God',
    'As for me, in the uprightness', 'O Lord God of Abraham', 'Except the Lord build the house',
    'Behold, I lay in Zion', 'Other foundation can no man lay', 'ARISE, O Lord, into Thy rest',
    'Then shall the King say unto them', 'PRAISE waiteth for Thee, O God', 'Blessed is the man whom Thou choosest',
    'The harvest truly is plenteous',
]

# Scripture sentences carry a citation in parentheses at the end, e.g. "(Psalm cxxiv. 8.)"
CITATION = re.compile(r'\((?:\d )?(?:Psalm|Isaiah|St\.|Hebrews|Lamentations|Revelation|Corinthians|1 Corinthians|'
                      r'1 Chronicles|Habakkuk|Micah|Malachi|Philippians|Romans|Ephesians|John|1 St\.)[^)]*\)\s*$')

# sections of short Scripture sentences without citations
SENTENCE_SECTIONS = [r'^Sentences$', r'^Morning$', r'^Evening$']


def is_fixed(block, context):
    if re.sub(r'^(?:<!--.*?-->\s*)+', '', block).lstrip().startswith('¶'):
        return False                               # rubrics are always modernized
    for h in context:
        if any(re.match(p, h) for p in FIXED_SECTIONS):
            return True
    body = re.sub(r'^(?:<!--.*?-->\s*)+', '', block).lstrip()
    if any(body.startswith(s) for s in FIXED_STARTS):
        return True
    if CITATION.search(body):
        return True
    if context and any(re.match(p, context[-1]) for p in SENTENCE_SECTIONS) and not body.startswith('¶'):
        return True
    return False
