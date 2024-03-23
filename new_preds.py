"""
Code for new predictions, based on first study.
"""
import csv
import re
from lingpy import Wordlist

wl_core = Wordlist('predictions/pred_core.tsv')
wl_ext = Wordlist('predictions/pred_extended.tsv')
both_wl = [wl_core, wl_ext]
exclude = ['full match', 'exclude', 'slight deviation']


def write_list(name, content):
    """Short function to write a list to a tsv-file."""
    with open(name, 'w', encoding='utf8', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerows(content)


def run_filter(regex, match=False):
    """Running a RegEx-filter on the wordlists."""
    output = [[
        'ID', 'Concept', 'Concepticon', 'ProtoTakana', 'ProtoPano_p',
        'predicted', 'form', 'meaning', 'evaluation'
        ]]

    for wl in both_wl:
        name = ''.join(['core' if wl == wl_core else 'extended'])
        for item in wl:
            pred = wl[item, 'predicted']
            idx = str(item) + '_' + name

            condition = regex.match(pred) if match is True else regex.search(pred)
            if condition and wl[item, 'evaluation'] not in exclude:
                output.append([
                    idx,
                    wl[item, 'concept'],
                    wl[item, 'concepticon'],
                    wl[item, 'prototakana'],
                    wl[item, 'protopano_p'],
                    wl[item, 'predicted'],
                    '', '', ''
                    ])
                print(wl[item])
    print('----')

    return output


# initial_b
bo = re.compile('β')
initial_b = run_filter(bo, match=True)
write_list('predictions/initial_b.tsv', initial_b)


# Fricative
fricative = re.compile('[a|i|ɨ|\\[i/ɨ\\|o][s|ʃ|ʂ][a|i|ɨ|\\[i/ɨ\\|o]')
intervocalic_fric = run_filter(fricative)
write_list('predictions/intervocalic.tsv', intervocalic_fric)


# Initial vowel drop
initial_i = re.compile('ɨ|\\[i/ɨ\\]')
initial_vowels = run_filter(initial_i, match=True)
write_list('predictions/initial_i.tsv', initial_vowels)

initial_a = re.compile('\\[a/hi\\]')
initial_vowels = run_filter(initial_a, match=True)
write_list('predictions/initial_a.tsv', initial_vowels)


# change of retroflexes
retrofl = re.compile('ɽ')
retroflexes = run_filter(retrofl)
write_list('predictions/retroflexes.tsv', retroflexes)

# change of friccatives
sche = re.compile('ʃ(?!\\])')
sche = run_filter(sche)
write_list('predictions/sche.tsv', sche)

# change of friccatives
se = re.compile('s(?!/)')
se = run_filter(se)
write_list('predictions/se.tsv', se)

# change of friccatives
se = re.compile('ɨ(?!])')
se = run_filter(se)
write_list('predictions/vowel-corr.tsv', se)
