"""
Code to group and ungroup segmens in comparative wordlists.
"""
from lingpy import Wordlist
import csv
from csvw.dsv import UnicodeDictReader
from unicodedata import normalize
from collections import defaultdict


def profile_sequence(string, segments, maxlen=None):
    if len(string) == 1:
        return string
    max_len = maxlen or max([len(x) for x in segments])
    
    # initialize queue
    queue = [([''], 0, string)]

    out = []
    while queue:
        current_sequence, length, rest = queue.pop(0)
        next_element = rest[0]
        combined_element = current_sequence[-1] + next_element
        clen = len(combined_element)

        if len(rest) > 1:
            if combined_element in segments or not current_sequence[-1] or clen < max_len:
                queue += [[
                    current_sequence[:-1]+[combined_element],
                    length,
                    rest[1:]
                    ]]
            if current_sequence[-1] in segments:
                queue += [[
                    current_sequence + [next_element],
                    length+1,
                    rest[1:]
                    ]]
        else:
            seqA = current_sequence[:-1]+[combined_element]
            seqB = current_sequence + [next_element]
            
            if not [x for x in seqA if (x not in segments and len(x) > 1)]:
                out += [seqA]
            if not [x for x in seqB if (x not in segments and len(x) > 1)]:
                out += [seqB]
    if out:
        return ' '.join(sorted(out, key=lambda x: len([y for y in x if y[0] !=
            '<']))[0])
    return ' '.join(['<{0}>'.format(x) if x in segments else
        x for x in string])

def get_profile(filename, delimiter="\t", space="_"):
    profile = {}
    with UnicodeDictReader(filename, delimiter=delimiter) as reader:
        for row in reader:
            profile[row["Grapheme"]] = row
    profile[space] = {k: "NULL" for k in row}
    return profile


def segment(sequence, profile, replace="IPA", space="_"):
    segments = set(profile)
    segmented = profile_sequence(normalize("NFC", space.join(sequence)), segments).split(" ")
    out = []
    for seg in segmented:
        rep = profile.get(seg, {replace: "«"+seg+"»"})[replace]
        if rep != "NULL":
            out += [rep]
    return out


PATH = '../cldf-data/girardprototakanan/cldf/parameters.csv'
concepts = defaultdict()
with UnicodeDictReader(PATH, delimiter=',') as reader:
    for line in reader:
        concepts[line["Name"]] = line['Concepticon_Gloss']


wl = Wordlist("prototakana.tsv")
prf = get_profile("profiles/takana_to_pano.tsv")

i = 1
D = {0: ["concept", "concepticon", "prototakana", "protopano", "doculect", "predicted", "form"]}
for idx, tokens_ in wl.iter_rows("tokens"):
    if wl[idx, "doculect"] == "ProtoTakana":
        PRED =  "".join(segment(tokens_, prf))
        D[i] = [wl[idx, "concept"], concepts[wl[idx, "concept"]], wl[idx, "form"], PRED, "Shipibo", "", ""]
        i += 1

# Convert from Proto-Pano prediction to Shipibo
wl = Wordlist(D)
prf = get_profile("profiles/pano_to_shipibo.tsv")
final_pred = [[
    "ID", "Concept", "Concepticon", "ProtoTakana", "ProtoPano_predicted", "Doculect", "Predicted", "Form"
]]

i = 1
for idx, tokens_ in wl.iter_rows("protopano"):
    PRED =  "".join(segment(tokens_, prf))
    if wl[idx, "concepticon"] != "":
        final_pred.append([idx, wl[idx, "concept"], wl[idx, "concepticon"], wl[idx, "prototakana"], wl[idx, "protopano"], "Shipibo", PRED, ""])
        i += 1

with open("predictions/predictions.tsv", 'w', encoding="utf8", newline='') as f:
    writer = csv.writer(f, delimiter="\t")
    writer.writerows(final_pred)
