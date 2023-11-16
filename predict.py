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


wl = Wordlist("data/girardprototakanan.tsv")
prf = SoundGrouper.from_file("profiles/takana_to_pano.tsv", delimiter="\t")

i = 0
D = {0: ["concept", "concepticon", "prototakana", "protopano", "doculect", "predicted", "form"]}
for idx, tokens in wl.iter_rows("tokens"):
    if wl[idx, "doculect"] == "ProtoTakana":
        i += 1
        PRED =  "".join(prf("".join(tokens), column="IPA"))
        D[i] = [
            wl[idx, "concept_name"],
            wl[idx, "concept"],
            "".join(wl[idx, "tokens"]),
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
    if tokens[0] == "a":
        tokens = list(tokens)
        tokens[0] = "^a"
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


############################################
# Compute intersections
def read_cl(path):
    concepts = defaultdict()
    with UnicodeDictReader(path, delimiter='\t') as reader:
        for line in reader:
            concepts[line["CONCEPTICON_GLOSS"]] = line['CONCEPTICON_ID']

    return concepts


def compute_intersec(cl1, cl2):
    intersecting = defaultdict()
    missing_from_cl1 = defaultdict()

    for idx in cl2:
        if idx in cl1:
            intersecting[idx] = cl2[idx]
        else:
            missing_from_cl1[idx] = cl2[idx]

    return intersecting, missing_from_cl1


############################################
# Read in data
PATH = 'cldf-data/concepticon/concepticondata/conceptlists/'
swadesh = read_cl(PATH + "Swadesh-1952-200.tsv")
conceptlists = {
    "oliveira": read_cl(PATH + "Oliveira-2014-517.tsv"),
    "girard": read_cl('cldf-data/girardprototakanan/etc/proto_concepts.tsv'),
    "valenzuela": read_cl('cldf-data/valenzuelazariquieypanotakana/etc/concepts.tsv')
}

predictions = Wordlist("predictions/full_predictions.tsv")
oliveira = Wordlist("data/oliveiraprotopanoan.tsv")
valenzuela = Wordlist("data/valenzuelazariquieypanotakana.tsv")

def extract_shared(preds, data, name):
    conceptlist = conceptlists[name]
    intersec, _ = compute_intersec(conceptlist, conceptlists["girard"])
    print(name, len(intersec))
    shared_forms = defaultdict()
    exclude = ["-", " ", "(", ")", "+"]
    for word in data:
        if data[word, "concept"] in intersec and data[word, "doculect"] in ["ShipiboKonibo", "SK"]:
            form = "".join([x for x in data[word, "alignment"] if x not in exclude])
            shared_forms[data[word, "concept"]] = form

    output_table = [[
        "ID", "Concept", "Concepticon", "ProtoTakana",
        "ProtoPano_predicted", "Doculect", "Predicted", "Form"
        ]]
    for word in preds:
        if preds[word, "concepticon"] in shared_forms:
            preds[word, "form"] = shared_forms[preds[word, "concepticon"]]
            output_table.append(preds[word])

    out = "predictions/shared_" + name + ".tsv"
    with open(out, 'w', encoding="utf8", newline='') as file:
        write_file = csv.writer(file, delimiter="\t")
        write_file.writerows(output_table)


extract_shared(predictions, oliveira, "oliveira")
extract_shared(predictions, valenzuela, "valenzuela")

count = 0
no_intersec = []
for item in predictions:
    count += 1
    concept = predictions[item, "concepticon"]
    if concept not in conceptlists["oliveira"] and concept not in conceptlists["valenzuela"] and concept != "None":
        no_intersec.append(predictions[item])

print("Total:", count)
with open("predictions/eval_predictions.tsv", 'w', encoding="utf8", newline='') as f:
    writer = csv.writer(f, delimiter="\t")
    writer.writerows(no_intersec)
