"""
Code to predict forms in Shipibo-Konibo based on forms in 
Proto-Takana, based on sound correspondences proposed by
Valenzuela & Zariquiey (2023), Girard (1971), and Oliveira (2014).
"""
from collections import defaultdict
import csv
from csvw.dsv import UnicodeDictReader
from lingpy import Wordlist
from grsn import SoundGrouper


PATH = '../cldf-data/girardprototakanan/cldf/parameters.csv'
concepts = defaultdict()
with UnicodeDictReader(PATH, delimiter=',') as reader:
    for line in reader:
        concepts[line["Name"]] = line['Concepticon_Gloss']


wl = Wordlist("prototakana.tsv")
prf = SoundGrouper.from_file("profiles/takana_to_pano.tsv", delimiter="\t")

i = 0
D = {0: ["concept", "concepticon", "prototakana", "protopano", "doculect", "predicted", "form"]}
for idx, tokens in wl.iter_rows("tokens"):
    if wl[idx, "doculect"] == "ProtoTakana":
        i += 1
        PRED =  "".join(prf("".join(tokens), column="IPA"))
        D[i] = [
            wl[idx, "concept"],
            concepts[wl[idx, "concept"]],
            wl[idx, "form"],
            PRED,
            "Shipibo",
            "",
            ""
            ]

# Convert from Proto-Pano prediction to Shipibo
wl = Wordlist(D)
prf = SoundGrouper.from_file("profiles/pano_to_shipibo.tsv", delimiter="\t")
final = [[
    "ID", "Concept", "Concepticon", "ProtoTakana",
    "ProtoPano_predicted", "Doculect", "Predicted", "Form"
]]

i = 0
for idx, tokens in wl.iter_rows("protopano"):
    PRED =  "".join(prf("".join(tokens), column="IPA"))
    if wl[idx, "concepticon"] != "":
        i += 1
        final.append([
            idx, wl[idx, "concept"],
            wl[idx, "concepticon"],
            wl[idx, "prototakana"],
            wl[idx, "protopano"],
            "Shipibo",
            "".join(PRED),
            ""
            ])

with open("predictions/full_predictions.tsv", 'w', encoding="utf8", newline='') as f:
    writer = csv.writer(f, delimiter="\t")
    writer.writerows(final)
