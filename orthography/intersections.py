"""This module computes the intersecs of conceptlists"""
import csv
from csvw.dsv import UnicodeDictReader
from collections import defaultdict
from lingpy import Wordlist


def read_cl(path):
    concepts = defaultdict()
    with UnicodeDictReader(path, delimiter='\t') as reader:
        for line in reader:
            concepts[line["CONCEPTICON_GLOSS"]] = line['CONCEPTICON_ID']

    return concepts


def read_wl(path):
    wordlist = Wordlist.from_cldf(
    path,
    # columns to be loaded from CLDF set
    columns=(
        "language_id",
        "concept_name",
        "concept_concepticon_gloss",
        "segments",
        "form",
        "alignment"
        ),
    # a list of tuples of source and target
    namespace=(
        ("language_id", "doculect"),
        ("concept_concepticon_gloss", "concept"),
        ("segments", "tokens")
        )
    )
    return wordlist


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
PATH = '../cldf-data/concepticon/concepticondata/conceptlists/'
swadesh = read_cl(PATH + "Swadesh-1952-200.tsv")
conceptlists = {
    "oliveira": read_cl(PATH + "Oliveira-2014-517.tsv"),
    "girard": read_cl('../cldf-data/girardprototakanan/etc/proto_concepts.tsv'),
    "valenzuela": read_cl('../cldf-data/valenzuelazariquieypanotakana/etc/concepts.tsv')
}

predictions = Wordlist("predictions/full_predictions.tsv")
oliveira = read_wl("../cldf-data/oliveiraprotopanoan/cldf/cldf-metadata.json")
valenzuela = read_wl("../cldf-data/valenzuelazariquieypanotakana/cldf/cldf-metadata.json")


def extract_shared(preds, data, name):
    conceptlist = conceptlists[name]
    intersec, _ = compute_intersec(conceptlist, conceptlists["girard"])

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

no_intersec = []
for item in predictions:
    concept = predictions[item, "concepticon"]
    if concept not in conceptlists["oliveira"] and concept not in conceptlists["valenzuela"]:
        no_intersec.append(predictions[item])

with open("predictions/eval_predictions.tsv", 'w', encoding="utf8", newline='') as f:
    writer = csv.writer(f, delimiter="\t")
    writer.writerows(no_intersec)
