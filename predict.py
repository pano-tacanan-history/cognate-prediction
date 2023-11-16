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
    "ID", "Concept", "Concepticon", "ProtoTakana", "ProtoPano_predicted",
    "Doculect", "Predicted", "Form", "Evaluation"
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
            "",
            ""
            ])

with open("predictions/full_predictions.tsv", 'w', encoding="utf8", newline='') as f:
    writer = csv.writer(f, delimiter="\t")
    writer.writerows(final)


############################################
# Compute intersections
def read_cl(path):
    """Reads in a conceptlist from a file."""
    concepts = defaultdict()
    with UnicodeDictReader(path, delimiter='\t') as reader:
        for line in reader:
            concepts[line["CONCEPTICON_GLOSS"]] = line['CONCEPTICON_ID']

    return concepts


def compute_intersec(cl1, cl2):
    """Computes the intersection of two conceptlists."""
    intersecting = defaultdict()
    missing_from_cl1 = defaultdict()

    for conc in cl2:
        if conc in cl1:
            intersecting[conc] = cl2[conc]
        else:
            missing_from_cl1[conc] = cl2[conc]

    return intersecting, missing_from_cl1


############################################
# Read in data
PATH = 'cldf-data/concepticon/concepticondata/conceptlists/'
conceptlists = {
    "oliveira": read_cl(PATH + "Oliveira-2014-517.tsv"),
    "girard": read_cl('cldf-data/girardprototakanan/etc/proto_concepts.tsv'),
    "valenzuela": read_cl('cldf-data/valenzuelazariquieypanotakana/etc/concepts.tsv')
}

predictions = Wordlist("predictions/full_predictions.tsv")
oliveira = Wordlist("data/oliveiraprotopanoan.tsv")
valenzuela = Wordlist("data/valenzuelazariquieypanotakana.tsv")

def extract_shared(data, name):
    """
    Extracts the shared concepts between the predictions and a dataset to a file.
    """
    # Original `predictions` gets overwritten by using the `insert` on the other variable.
    # Unclear why this is the case, but as a workaround, one can reload the predictions.
    dataset = Wordlist("predictions/full_predictions.tsv")
    conceptlist = conceptlists[name]
    intersec, _ = compute_intersec(conceptlist, conceptlists["girard"])
    shared_forms = defaultdict()
    exclude = ["-", " ", "(", ")", "+"]
    for word in data:
        if data[word, "concept"] in intersec and data[word, "doculect"] in ["ShipiboKonibo", "SK"]:
            form = "".join([x for x in data[word, "alignment"] if x not in exclude])
            shared_forms[data[word, "concept"]] = form

    output_table = [[
        "ID", "Concept", "Concepticon", "ProtoTakana", "ProtoPano_predicted",
        "Doculect", "Predicted", "Form", "Evaluation"
        ]]
    for word in dataset:
        if dataset[word, "concepticon"] in shared_forms:
            dataset[word, "form"] = shared_forms[dataset[word, "concepticon"]]
            mod_data = dataset[word]
            mod_data.insert(0, word)
            output_table.append(mod_data)

    out = "predictions/shared_" + name + ".tsv"
    with open(out, 'w', encoding="utf8", newline='') as file:
        write_file = csv.writer(file, delimiter="\t")
        write_file.writerows(output_table)


extract_shared(valenzuela, "valenzuela")
extract_shared(oliveira, "oliveira")

no_intersec = [[
        "ID", "Concept", "Concepticon", "ProtoTakana", "ProtoPano_predicted",
        "Doculect", "Predicted", "Form", "Evaluation"
        ]]

lists = [conceptlists["oliveira"], conceptlists["valenzuela"]]
COUNT = 0
for item in predictions:
    concept = predictions[item, "concepticon"]
    if all(concept not in x for x in lists) and concept != "None":
        COUNT += 1
        pred = predictions[item]
        pred.insert(0, item)
        no_intersec.append(pred)

print("In total, there are", COUNT, "predictions to evaluate.")

with open("predictions/eval_predictions.tsv", 'w', encoding="utf8", newline='') as f:
    writer = csv.writer(f, delimiter="\t")
    writer.writerows(no_intersec)
